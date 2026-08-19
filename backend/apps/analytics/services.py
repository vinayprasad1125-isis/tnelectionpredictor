from django.db.models import Sum, Count, F, Max
from apps.elections.models import Election, ElectionResult
from apps.constituencies.models import Constituency

class AnalyticsService:
    @staticmethod
    def get_party_performance(year=None):
        """
        Returns total votes and seats won by each party for a given year.
        """
        qs = ElectionResult.objects.all()
        if year:
            qs = qs.filter(election__year=year)
            
        # Total state votes for the year
        total_state_votes = qs.aggregate(total=Sum('votes_received'))['total'] or 1
        
        # Party aggregations
        party_stats = qs.values('party__abbreviation').annotate(
            total_votes=Sum('votes_received'),
            seats_won=Count('id', filter=F('is_winner'))
        ).order_by('-seats_won', '-total_votes')
        
        # Calculate vote share
        for stat in party_stats:
            stat['vote_share'] = round((stat['total_votes'] / total_state_votes) * 100, 2)
            
        return list(party_stats)

    @staticmethod
    def get_constituency_history(constituency_id):
        """
        Returns the historical results for a specific constituency.
        """
        results = ElectionResult.objects.filter(
            constituency_id=constituency_id,
            is_winner=True
        ).select_related('election', 'party', 'candidate').order_by('-election__year')
        
        history = []
        for r in results:
            history.append({
                'year': r.election.year,
                'candidate': r.candidate.name,
                'party': r.party.abbreviation,
                'votes': r.votes_received,
                'margin': r.winning_margin,
                'vote_share': r.vote_percentage
            })
        return history

    @staticmethod
    def get_vote_share_trends(party_abbr):
        """
        Returns the historical vote share trend for a specific party across all elections.
        """
        # Get total votes per year
        total_votes_per_year = list(ElectionResult.objects.values('election__year').annotate(
            total=Sum('votes_received')
        ).order_by('election__year'))
        
        # Get party votes per year
        party_votes_per_year = list(ElectionResult.objects.filter(party__abbreviation=party_abbr).values('election__year').annotate(
            party_total=Sum('votes_received')
        ).order_by('election__year'))
        
        party_dict = {item['election__year']: item['party_total'] for item in party_votes_per_year}
        
        trends = []
        for item in total_votes_per_year:
            year = item['election__year']
            total = item['total'] or 1
            party_votes = party_dict.get(year, 0)
            trends.append({
                'year': year,
                'vote_share': round((party_votes / total) * 100, 2)
            })
        return trends

    @staticmethod
    def get_seat_trends(party_abbr):
        """
        Returns the historical seat count trend for a specific party.
        """
        trends_qs = ElectionResult.objects.filter(
            party__abbreviation=party_abbr, 
            is_winner=True
        ).values('election__year').annotate(
            seats_won=Count('id')
        ).order_by('election__year')
        
        return [{'year': item['election__year'], 'seats_won': item['seats_won']} for item in trends_qs]

    @staticmethod
    def get_turnout():
        """
        Returns the overall historical vote turnout (total votes cast).
        """
        trends_qs = ElectionResult.objects.values('election__year').annotate(
            total_votes=Sum('votes_received')
        ).order_by('election__year')
        
        return [{'year': item['election__year'], 'total_votes': item['total_votes']} for item in trends_qs]
