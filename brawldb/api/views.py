from rest_framework.generics import ListAPIView
from .serializers import ComboSerializer
from main.models import Combo, Legend
from django.db.models import Q


class CombosListView(ListAPIView):
    serializer_class = ComboSerializer

    def get_queryset(self):
        qs = Combo.objects.select_related('legend', 'weapon')
        params = self.request.query_params
        if 'legend' in params:
            legend = Legend.objects.get(name__iexact=params['legend'])
            qs = qs.filter(Q(legend=legend) | Q(legend__isnull=True)).filter(weapon__in=[weapon.id for weapon in legend.weapons.all()]).filter(Q(dexterity__lte=legend.dexterity + 1) | Q(dexterity__isnull=True))
        if 'weapon' in params:
            qs = qs.filter(weapon__name__iexact=params['weapon'])
        if 'order_by' in params:
            qs = qs.order_by(params['order_by'])
        return qs