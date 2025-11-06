from typing import List

from .models import Lead


class LeadRepository:
    def __init__(self) -> None:
        self._leads: List[Lead] = []

    def add(self, lead: Lead) -> None:
        self._leads.append(lead)

    def list(self) -> List[Lead]:
        return list(self._leads)


