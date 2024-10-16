from rest_framework import serializers
from main.models import Combo, Legend, Weapon


class ComboSerializer(serializers.ModelSerializer):
    legend = serializers.CharField(source='legend.name', allow_null=True)
    weapon = serializers.CharField(source='weapon.name')
    attack_string = serializers.CharField(source='__str__')
    absolute_url = serializers.CharField(source='get_absolute_url')

    class Meta:
        model = Combo
        fields = ['legend', 'weapon', 'video', 'usability', 'attack_string', 'start_damage', 'stop_damage', 'dexterity', 'average_damage', 'absolute_url']

