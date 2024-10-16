from django.db.models.signals import m2m_changed, post_save
from django.dispatch import receiver
from .models import Combo

@receiver(m2m_changed, sender=Combo.attacks.through)
def combo_attacks_changed(sender, instance, action, **kwargs):
    if action == 'post_add':
        dependents = instance.get_dependents()
        if dependents:
            for dependent in dependents:
                dependent.dependencies.add(instance)
            instance.refresh_from_db()
            for dependent in instance.dependents.all():
                dependent.check_dependencies()
        dependencies = instance.get_dependencies()
        instance.dependencies.set(dependencies)
        instance.set_titles()
        instance.save(skip_logging=True)