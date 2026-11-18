from miso_corners import Task as Base
from robust_metrics import apply_directions

class Task(Base):
    def __init__(self,profile='search_full'):
        super().__init__(profile)
        apply_directions(self.cfg['constraints'])
        self.cfg['description'] += ' November10: lower power and noise accepted; other original matching bands retained.'
