from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Count, F, Max
from django.urls import reverse

class User(AbstractUser):
    ...

class BaseModel(models.Model):
    name = models.CharField(max_length=32)

    class Meta:
        abstract = True

    def __str__(self):
        return self.name

class Legend(BaseModel):
    weapons = models.ManyToManyField('Weapon', blank=True, related_name='legends')
    dexterity = models.IntegerField(default=5)

    def icon(self):
        return f'/static/legends/{self.name.upper().replace(" ","")}_Icon.png'

class Weapon(BaseModel):

    def icon(self):
        return f'/static/weapons/{self.name.lower().replace(" ", "_")}_icon.png'

class Attack(models.Model):
    move = models.ForeignKey('Move', related_name='attacks', on_delete=models.CASCADE)
    modifiers = models.ManyToManyField('Modifier', blank=True, related_name='attacks')
    order = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f'{self.move} ({self.order})'

class Move(BaseModel):
    is_movement = models.BooleanField(default=False)
    is_signature = models.BooleanField(default=False)
    description = models.TextField(blank=True, null=True)

class Modifier(BaseModel):
    abbr = models.CharField(max_length=4)
    description = models.TextField()

def upload_to_combo(instance, filename):
    combo_id = 1
    ext = filename.split('.')[-1]
    try:
        combo_id = Combo.objects.latest('id').id + 1
    except Combo.DoesNotExist:
        pass
    return f'combos/{instance.weapon.name.lower()}/{combo_id}.{ext}'

DAMAGE_COLORS = {
            '0' : '#ffffff',
            '10' : '#ffffcc',
            '20' : '#ffff99',
            '30' : '#ffff66',
            '40' : '#ffff33',
            '50' : '#ffff00',
            '60' : '#ffea00',
            '70' : '#ffd600',
            '80' : '#ffc100',
            '90' : '#ffad00',
            '100' : '#ff9900',
            '110' : '#ff7a00',
            '120' : '#ff5b00',
            '130' : '#ff3d00',
            '140' : '#ff1e00',
            '150' : '#ff0000',
            '160' : '#f20000',
            '170' : '#e50000',
            '180' : '#d80000',
            '190' : '#cb0000',
            '200' : '#bf0000',
            '210' : '#b40000',
            '220' : '#aa0000',
            '230' : '#a00000',
            '240' : '#960000',
            '250' : '#8c0000'
        }

class Combo(models.Model):
    outdated = models.BooleanField(default=False)
    dependencies = models.ManyToManyField('Combo', blank=True, related_name='dependents')
    legend = models.ForeignKey('Legend', blank=True, null=True, related_name='combos', on_delete=models.SET_NULL)
    weapon = models.ForeignKey('Weapon', blank=True, null=True, related_name='combos', on_delete=models.SET_NULL)
    video = models.FileField(upload_to=upload_to_combo)
    usability = models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(10)])
    attacks = models.ManyToManyField('attack', blank=True, related_name='combos')
    start_damage = models.IntegerField(default=0)
    stop_damage = models.IntegerField(blank=True, null=True)
    dexterity = models.IntegerField(blank=True, null=True, validators=[MinValueValidator(1), MaxValueValidator(10)])
    average_damage = models.IntegerField(default=0)

    class Meta:
        ordering = ['-usability']

    def __str__(self):
        name = ''
        for attack in self.attacks.prefetch_related('modifiers'):
            base = attack.move.name
            modifiers = ''
            for modifier in attack.modifiers.all():
                modifiers += f'({modifier.abbr}) '
            modifiers = modifiers.rstrip()
            name += f'{base} {modifiers} > '
        name = f'{self.weapon.name} | {name.rstrip(" > ")}'
        if self.legend:
            name = f'{self.legend} ' + name
        return name

    def get_absolute_url(self):
        return reverse('combo', kwargs={'pk': self.id})

    def dexterity_display(self):
        if not self.dexterity:
            return 'Any'
        return f'{self.dexterity}+'

    def damage_display(self):
        if not self.stop_damage:
            return f'{self.start_damage}+'
        return f'{self.start_damage}-{self.stop_damage}'

    def usability_color(self):
        colors = {
            "1": "#FF0000",
            "2": "#FF3300",
            "3": "#FF6600",
            "4": "#FF9900",
            "5": "#FFCC00",
            "6": "#FFFF00",
            "7": "#CCFF00",
            "8": "#99FF00",
            "9": "#66FF00",
            "10": "#33FF00"
        }
        return colors[str(self.usability)]

    def start_damage_color(self):
        return DAMAGE_COLORS[str(self.start_damage)]

    def stop_damage_color(self):
        return DAMAGE_COLORS[str(self.stop_damage)]

    def get_dependencies(self):
        attacks = self.attacks.all()
        dependencies = []
        i = 0
        while i <= len(attacks):
            combos = Combo.objects.annotate(num_attacks=Count('attacks')).filter(weapon=self.weapon)
            current_attacks = []
            non_movement_attacks_counted = 0
            attacks_counted = 0
            for j in range(i, len(attacks)):
                attacks_counted += 1
                attack = attacks[j]
                current_attacks.append((attack, attacks_counted))
                if not attack.move.is_movement:
                    non_movement_attacks_counted += 1
                if non_movement_attacks_counted == 2:
                    break
            i += 1
            for attack, order in current_attacks:
                combos = combos.filter(attacks__move=attack.move, attacks__order=order)
            combos = combos.filter(num_attacks=attacks_counted).exclude(id=self.id)
            if self.legend and any([attack.move.is_signature for attack, order in current_attacks]):
                print(f'Sig combo! {current_attacks}')
                combos = combos.filter(legend=self.legend)
            if len(combos) > 0:
                dependencies += list(combos)
        return dependencies

    def get_dependents(self):
        attacks = self.attacks.all()
        print(attacks)
        non_movement_attacks = 0
        for attack in attacks:
            if not attack.move.is_movement:
                non_movement_attacks += 1
        print(non_movement_attacks)
        if non_movement_attacks > 2:
            return

        dependents = []
        combos = Combo.objects.filter(weapon=self.weapon)
        if self.legend and self.attacks.filter(move__is_signature=True).exists():
            combos = combos.filter(legend=self.legend)
        order = 1
        first_attack = attacks[0]
        for attack in attacks:
            combos = combos.filter(attacks__move=attack.move)
        for combo in combos:
            if combo == self:
                continue
            combo_valid = True
            order = combo.attacks.get(move=first_attack.move).order
            for attack in attacks[1:]:
                attack = combo.attacks.get(move=attack.move)
                if attack.order != order + 1:
                    combo_valid = False
                    break
                order += 1
            if combo_valid:
                dependents.append(combo)
        return dependents

    def check_dependencies(self):
        print(self)
        dexterity = self.dependencies.aggregate(Max('dexterity'))['dexterity__max']
        outdated = self.dependencies.filter(outdated=True).exists()
        print(dexterity, outdated)
        self.dexterity = dexterity
        self.outdated = outdated
        self.save()

    def save(self, *args, **kwargs):
        has_changed = False
        if self.id:
            previous_save = Combo.objects.get(id=self.id)
            fields = [field for field in self._meta.get_fields() if not ((field.auto_created and field.is_relation) or isinstance(field, (models.ForeignKey, models.ManyToManyField)))]
            patch = Patch.objects.latest('id')
            for field in fields:
                previous_value = getattr(previous_save, field.name)
                current_value = getattr(self, field.name)
                if previous_value != current_value:
                    has_changed = True
                    change = Change(patch=patch, combo=self, type=field.name)
                    if isinstance(field, (models.IntegerField, models.PositiveIntegerField)):
                        change.from_value = previous_value
                        change.to_value = current_value
                    elif field.name == 'outdated' and current_value == True:
                        change.type = 'outdated'
                    else:
                        change.type ='working'
                    change.save()
        super().save(*args, **kwargs)
        if has_changed:
            for dependent in self.dependents.all():
                dependent.check_dependencies()

class Patch(models.Model):
    number = models.CharField(max_length=12)
    link = models.URLField(blank=True, null=True)

    def __str__(self):
        return self.number

class Change(models.Model):
    patch = models.ForeignKey('Patch', related_name='changes', on_delete=models.CASCADE)
    combo = models.ForeignKey('Combo', related_name='changes', on_delete=models.CASCADE)
    type = models.CharField(max_length=64)
    from_value = models.IntegerField(blank=True, null=True)
    to_value = models.IntegerField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True)

    def type_pretty(self):
        return self.type.replace('_', ' ').title()

    def __str__(self):
        base = f'{self.patch.number} | {self.combo.__str__()} | {self.type}'
        if self.type not in ['working', 'outdated']:
            base += f' | {self.from_value} to {self.to_value}'
        return base