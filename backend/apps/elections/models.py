from django.db import models

class Election(models.Model):
    ELECTION_TYPES = [
        ('ASSEMBLY', 'State Assembly'),
        ('LOK_SABHA', 'Lok Sabha'),
        ('LOCAL_BODY', 'Local Body'),
    ]

    year = models.IntegerField(help_text="Year of the election")
    election_type = models.CharField(max_length=20, choices=ELECTION_TYPES, default='ASSEMBLY')
    state = models.CharField(max_length=100, default='Tamil Nadu')
    date = models.DateField(null=True, blank=True, help_text="Exact date of the election if available")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-year', 'election_type']
        unique_together = ['year', 'election_type', 'state']

    def __str__(self):
        return f"{self.year} {self.get_election_type_display()} - {self.state}"


class ElectionResult(models.Model):
    election = models.ForeignKey(Election, on_delete=models.CASCADE, related_name='results')
    constituency = models.ForeignKey('constituencies.Constituency', on_delete=models.CASCADE, related_name='results')
    candidate = models.ForeignKey('candidates.Candidate', on_delete=models.CASCADE, related_name='results')
    party = models.ForeignKey('parties.Party', on_delete=models.CASCADE, related_name='results')

    votes_received = models.IntegerField(default=0)
    vote_percentage = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    
    is_winner = models.BooleanField(default=False)
    winning_margin = models.IntegerField(null=True, blank=True)
    
    turnout_percentage = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, help_text="Voter turnout for this constituency in this election")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['election', 'constituency', '-votes_received']
        unique_together = ['election', 'constituency', 'candidate']

    def __str__(self):
        return f"{self.candidate.name} - {self.constituency.name} ({self.election.year})"
