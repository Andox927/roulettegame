import random
from typing import List, Tuple

from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpRequest, HttpResponse
from django.shortcuts import redirect, render
from django.views.decorators.http import require_POST

from .models import DrawHistory, Prize, RouletteConfig, AwardList, AwardHistory

ANGLE_OFFSET = -90.0

PALETTE = [
    '#F59E0B',
    '#FDE047',
    '#86EFAC',
    '#22C55E',
    '#A7F3D0',
    '#FCD34D',
    '#FDBA74',
    '#F97316',
    '#FCA5A5',
    '#FB7185',
    '#FBBF24',
    '#4ADE80',
]


def build_segments(prizes: List[Prize]) -> Tuple[str, List[dict], List[dict]]:
    usable = [p for p in prizes if p.probability and p.probability > 0]
    total = sum(p.probability for p in usable)
    if total <= 0:
        return "conic-gradient(#E5E7EB 0deg 360deg)", [], []

    segments = []
    gradient_parts = []
    start = 0.0
    color_idx = 0
    for prize in usable:
        angle = prize.probability / total * 360.0
        end = start + angle
        color = PALETTE[color_idx % len(PALETTE)]
        gradient_parts.append(f"{color} {start:.2f}deg {end:.2f}deg")
        segments.append({
            'prize': prize,
            'start': start,
            'end': end,
            'mid': (start + end) / 2.0,
        })
        start = end
        color_idx += 1

    gradient = f"conic-gradient(from {ANGLE_OFFSET}deg, " + ", ".join(gradient_parts) + ")"
    labels = []
    for s in segments:
        angle = s['end'] - s['start']
        name = s['prize'].name
        length = max(1, len(name))
        if angle >= 40:
            base = 14
            radius = 104
        elif angle >= 25:
            base = 12
            radius = 96
        else:
            base = 10
            radius = 88
        size = max(9, base - max(0, length - 4))
        radius = max(78, radius - max(0, length - 4) * 4)
        display_angle = (s['mid'] + ANGLE_OFFSET) % 360
        labels.append({
            'name': name,
            'chars': list(name),
            'angle': display_angle,
            'font_size': size,
            'radius': radius,
        })
    return gradient, labels, segments


def frontend(request: HttpRequest) -> HttpResponse:
    configs = list(RouletteConfig.objects.all().order_by('-updated_at'))
    config_id = request.GET.get('config')
    selected = None
    if config_id:
        selected = RouletteConfig.objects.filter(id=config_id).first()
    if selected is None and configs:
        selected = configs[0]

    prizes = list(selected.prizes.all()) if selected else []
    wheel_gradient, labels, _ = build_segments(prizes)
    if selected:
        DrawHistory.objects.filter(config=selected).delete()
    history = list(DrawHistory.objects.filter(config=selected)[:50]) if selected else []

    context = {
        'configs': configs,
        'selected': selected,
        'wheel_gradient': wheel_gradient,
        'labels': labels,
        'history': history,
    }
    return render(request, 'frontend.html', context)


@login_required
def backend(request: HttpRequest) -> HttpResponse:
    configs = list(RouletteConfig.objects.all().order_by('-updated_at'))
    config_id = request.GET.get('config') or request.POST.get('config_id')
    selected = None
    if config_id:
        selected = RouletteConfig.objects.filter(id=config_id).first()
    if selected is None and configs:
        selected = configs[0]

    if request.method == 'POST':
        name = (request.POST.get('config_name') or '').strip()
        config_id = request.POST.get('config_id')
        if config_id:
            config = RouletteConfig.objects.filter(id=config_id).first()
            if config:
                config.name = name or config.name
                config.save()
            else:
                config = RouletteConfig.objects.create(name=name or '未命名抽獎')
        else:
            config = RouletteConfig.objects.create(name=name or '未命名抽獎')

        names = request.POST.getlist('prize_name')
        probs = request.POST.getlist('prize_prob')
        Prize.objects.filter(config=config).delete()
        for idx, (n, p) in enumerate(zip(names, probs)):
            n = (n or '').strip()
            p = (p or '').strip()
            if not n or not p:
                continue
            try:
                prob = float(p)
            except ValueError:
                continue
            Prize.objects.create(config=config, name=n, probability=prob, order=idx)

        return redirect(f'/backend/?config={config.id}')

    prizes = list(selected.prizes.all()) if selected else []
    activity_list = list(AwardList.objects.all())
    activity_name = request.GET.get('activity')
    activity_detail = None
    activity_history = []
    if activity_name:
        activity_detail = AwardList.objects.filter(activity_name=activity_name).first()
        if activity_detail:
            activity_history = list(AwardHistory.objects.filter(activity=activity_detail))
    context = {
        'configs': configs,
        'selected': selected,
        'prizes': prizes,
        'activity_list': activity_list,
        'activity_detail': activity_detail,
        'activity_history': activity_history,
    }
    return render(request, 'backend.html', context)


@require_POST
def api_draw(request: HttpRequest) -> JsonResponse:
    config_id = request.POST.get('config_id')
    nickname = (request.POST.get('nickname') or '').strip()
    if not config_id or not nickname:
        return JsonResponse({'success': False, 'message': '請輸入暱稱並選擇抽獎內容'})

    config = RouletteConfig.objects.filter(id=config_id).first()
    if not config:
        return JsonResponse({'success': False, 'message': '找不到抽獎內容'})

    prizes = list(config.prizes.all())
    wheel_gradient, labels, segments = build_segments(prizes)
    if not segments:
        return JsonResponse({'success': False, 'message': '尚未設定獎項或機率'})

    total = sum(s['prize'].probability for s in segments)
    r = random.uniform(0, total)
    acc = 0.0
    selected = segments[-1]
    for seg in segments:
        acc += seg['prize'].probability
        if r <= acc:
            selected = seg
            break

    DrawHistory.objects.create(
        config=config,
        nickname=nickname,
        prize_name=selected['prize'].name,
    )

    history = list(DrawHistory.objects.filter(config=config)[:50])
    history_payload = [
        {
            'time': h.created_at.astimezone().strftime('%H:%M'),
            'prize': h.prize_name,
            'nickname': h.nickname,
        }
        for h in history
    ]

    start_angle = selected['start']
    end_angle = selected['end']
    span = max(0.0, end_angle - start_angle)
    pad = min(2.0, span * 0.2)
    if pad * 2 >= span:
        pad = 0.0
    landed_angle = random.uniform(start_angle + pad, end_angle - pad) if span > 0 else 0.0

    return JsonResponse({
        'success': True,
        'prize': selected['prize'].name,
        'target_angle': round((landed_angle + ANGLE_OFFSET) % 360, 2),
        'history': history_payload,
    })


@login_required
@require_POST
def api_new_activity(request: HttpRequest) -> JsonResponse:
    activity_name = (request.POST.get('activity_name') or '').strip()
    config_id = request.POST.get('config_id')
    if not activity_name:
        return JsonResponse({'success': False, 'message': '請輸入活動名稱'})

    config = RouletteConfig.objects.filter(id=config_id).first()
    if not config:
        return JsonResponse({'success': False, 'message': '找不到抽獎內容'})

    if AwardList.objects.filter(activity_name=activity_name).exists():
        return JsonResponse({'success': False, 'message': '活動名稱已存在，請更換名稱'})

    activity = AwardList.objects.create(activity_name=activity_name, config=config)
    draws = list(DrawHistory.objects.filter(config=config))
    histories = [
        AwardHistory(
            activity=activity,
            nickname=draw.nickname,
            prize_name=draw.prize_name,
            drawn_at=draw.created_at,
        )
        for draw in draws
    ]
    if histories:
        AwardHistory.objects.bulk_create(histories)
    DrawHistory.objects.filter(config=config).delete()

    return JsonResponse({'success': True})


@login_required
@require_POST
def api_delete_activity(request: HttpRequest) -> JsonResponse:
    activity_name = (request.POST.get('activity_name') or '').strip()
    if not activity_name:
        return JsonResponse({'success': False, 'message': '缺少活動名稱'})

    activity = AwardList.objects.filter(activity_name=activity_name).first()
    if not activity:
        return JsonResponse({'success': False, 'message': '找不到活動'})

    activity.delete()
    return JsonResponse({'success': True})


@require_POST
def logout_view(request: HttpRequest) -> HttpResponse:
    logout(request)
    return redirect('/')
