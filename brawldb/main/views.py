from typing import Any
from django.shortcuts import render
from django.views.generic import TemplateView
from django.core.paginator import Paginator
from django.views.decorators.csrf import csrf_exempt
from .models import Combo, Legend, Weapon, Move, Modifier, Attack, Patch, Change
from django.db.models import Q, Prefetch
from django.contrib.admin.views.decorators import staff_member_required

def clean_request_body(request_body):
    request_body = request_body.copy()
    for key, value in request_body.items():
        if value == '':
            request_body[key] = None
    return request_body

class Home(TemplateView):
    template_name = 'home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({'combo_count': Combo.objects.count(), 'patch': Patch.objects.latest('id')})
        return context

@staff_member_required
@csrf_exempt
def combos_add(request):
    if request.method == "POST":
        post = clean_request_body(request.POST)
        print(post['legend'])
        cleaned_attacks = [{'move' : post[f'attack_{key.split("_")[-1]}'], 'modifiers' : post.getlist(f'modifier_{key.split("_")[-1]}')} for key in post if 'attack_' in key]
        attacks = []
        for order, data in enumerate(cleaned_attacks, start=1):
            move = Move.objects.get(id=data['move'])
            attack = Attack.objects.create(move=move, order=order)
            attack.modifiers.set(data['modifiers'])
            attacks.append(attack.id)
        video = request.FILES['video']
        legend = Legend.objects.get(id=post['legend']) if post['legend'] else None
        weapon = Weapon.objects.get(id=post['weapon'])
        usability = post['usability']
        start_damage = post['start_damage']
        stop_damage = post['stop_damage']
        dexterity = post['dexterity']
        average_damage = post['average_damage']
        combo = Combo.objects.create(video=video, legend=legend, weapon=weapon, usability=usability, start_damage=start_damage, stop_damage=stop_damage, dexterity=dexterity, average_damage=average_damage)
        combo.attacks.set(attacks)
    context = {'moves' : Move.objects.all(), 'modifiers' : Modifier.objects.all(), 'weapons' : Weapon.objects.all(), 'legends': Legend.objects.all()}
    return render(request, 'combos/combo-add.html', context)

def combos(request):
    combos = Combo.objects.filter(outdated=False)
    template = 'combos/combos.html'
    if 'form_submitted' in request.GET:
        template = 'mixins/combos.html'
        show_outdated_combos = request.GET.get('show_outdated_combos')
        show_sig_combos = request.GET.get('show_sig_combos')
        if show_outdated_combos:
            combos = Combo.objects.all()
        if not show_sig_combos:
            combos = combos.filter(legend__isnull=True)
        if 'legend' in request.GET:
            legend = Legend.objects.get(id=request.GET['legend'])
            combos = combos.filter(Q(legend=legend) | Q(legend__isnull=True)).filter(weapon__in=[weapon.id for weapon in legend.weapons.all()]).filter(Q(dexterity__lte=legend.dexterity + 1) | Q(dexterity__isnull=True))
        if 'weapon' in request.GET:
            combos = combos.filter(weapon=request.GET['weapon'])
        if 'order_by' in request.GET:
            combos = combos.order_by(request.GET['order_by'])
    paginator = Paginator(combos, 20)
    page_number = request.GET.get('page', 1)
    page = paginator.get_page(page_number)
    context = {'combos' : page.object_list, 'page' : page, 'weapons' : Weapon.objects.all(), 'legends': Legend.objects.all(), 'modifiers': Modifier.objects.all(), 'combos_count': combos.count()}
    return render(request, template, context)

def patches(request):
    patch = Patch.objects.latest('id')
    if 'patch' in request.GET:
        patch = Patch.objects.get(number=request.GET['patch'])
    context = {'patch_numbers': Patch.objects.values_list('number', flat=True), 'patch': patch, 'general_changes': Change.objects.filter(combo=None, patch=patch), 'combos': Combo.objects.prefetch_related(Prefetch('changes', queryset=Change.objects.filter(patch=patch), to_attr='current_patch_changes')).filter(changes__patch=patch).distinct()}
    return render(request, 'patches.html', context)

def combo(request, pk):
    combo = Combo.objects.get(pk=pk)
    context = {'combo' : combo, 'patches': Patch.objects.prefetch_related(Prefetch('changes', queryset=Change.objects.filter(combo=combo), to_attr='combo_changes')).filter(changes__combo=combo).distinct()}
    return render(request, 'combos/combo.html', context)

def terminology(request):
    context = {'moves': Move.objects.all(), 'modifiers': Modifier.objects.all()}
    return render(request, 'terminology.html', context)