from rest_framework import serializers
from .models import Election, ElectionResult
from apps.constituencies.serializers import ConstituencySerializer
from apps.candidates.serializers import CandidateSerializer
from apps.parties.serializers import PartySerializer

class ElectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Election
        fields = '__all__'

class ElectionResultSerializer(serializers.ModelSerializer):
    constituency_name = serializers.ReadOnlyField(source='constituency.name')
    candidate_name = serializers.ReadOnlyField(source='candidate.name')
    election_year = serializers.ReadOnlyField(source='election.year')

    class Meta:
        model = ElectionResult
        fields = '__all__'

class ElectionResultDetailSerializer(serializers.ModelSerializer):
    election = ElectionSerializer(read_only=True)
    constituency = ConstituencySerializer(read_only=True)
    candidate = CandidateSerializer(read_only=True)
    party = PartySerializer(read_only=True)

    class Meta:
        model = ElectionResult
        fields = '__all__'
