from posts.models import Interaction
from bots import models

labels = dict(dudas_peque='faqs', faqs='faqs', etapas_afini='afini_levels', afini_levels='afini_levels',
              explorar_beneficios_selec="explore_benefits", explore_benefits='explore_benefits',
              unregistered='start_registration', start_registration='start_registration',
              finished_register='finish_registration', finish_registration='finish_registration',
              actividades_nr='more_activities', more_activities='more_activities',
              assesment_init='assesment_init', star_trial_premium='start_trial_premium',
              start_trial_premium='start_trial_premium', lead_premium='lead_premium',
              trial_premium_complete='trial_premium_complete', interes_premium1='lead_premium')


def run():
    filtered_labels = [a for a in labels]
    print(filtered_labels)
    filtered_interactions = Interaction.objects.filter(type__in=filtered_labels)
    for i in filtered_interactions:
        bot_interaction = models.Interaction.objects.get(name=labels[i.type])
        new_interaction = models.UserInteraction.objects.create(interaction=bot_interaction, user_id=i.user_id,
                                                                bot_id=i.bot_id, value=i.value,
                                                                created_at=i.created_at, updated_at=i.updated_at)
        print(i.pk)
        i.delete()
        print(new_interaction)
