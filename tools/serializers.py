from rest_framework import serializers


class APISerializer(serializers.ModelSerializer):

    def to_representation(self, instance):
        
        success = True
        payload = instance

        if isinstance(instance, dict):
            if 'success' in instance:
                success = instance.pop('success')
            if 'payload' in instance:
                payload = instance.pop('payload')
            if 'reason' in instance:
                reason = instance.pop('reason')
                self.context['reason'] = reason
            
        self.context['success'] = success
        return dict(self.context, **{
            'payload': payload
        })