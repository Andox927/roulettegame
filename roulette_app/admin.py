from django.contrib import admin
from .models import RouletteConfig, Prize, DrawHistory, AwardList, AwardHistory


class PrizeInline(admin.TabularInline):
    model = Prize
    extra = 0


@admin.register(RouletteConfig)
class RouletteConfigAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'updated_at')
    inlines = [PrizeInline]


@admin.register(DrawHistory)
class DrawHistoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'config', 'nickname', 'prize_name', 'created_at')
    list_filter = ('config',)


@admin.register(AwardList)
class AwardListAdmin(admin.ModelAdmin):
    list_display = ('activity_name', 'config', 'created_at')
    list_filter = ('config',)


@admin.register(AwardHistory)
class AwardHistoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'activity', 'nickname', 'prize_name', 'drawn_at')
    list_filter = ('activity',)


@admin.register(Prize)
class PrizeAdmin(admin.ModelAdmin):
    list_display = ('id', 'config', 'name', 'probability', 'order')
    list_filter = ('config',)
