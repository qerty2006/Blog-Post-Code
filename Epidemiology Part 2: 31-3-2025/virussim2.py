import networkx as nx
import random
from typing import List, Dict, Tuple, Union, Callable
import os
import matplotlib as plotty
import time


class Virus:
    """
    Virus will have the following components:
    - Incubation period V.incubation_period: int
    - Transmission method:
        Infectious to connection probabilities V.infectious: [float]
        Connection to Contraction probabilities V.contract: [float]
        Mask effectiveness V.effectiveness": [float]

    - Recovery and Death probabilities V.recovery: float, V.death: float

    - Immunocompromised modifiers V.immuno: Dict[str, float]:
        Infection rate modifier V.immuno["infection"]: float
        Contraction rate modifier V.immuno["contraction"]: float
        Recovery rate modifier V.immuno["recovery"]: float
        Death rate modifier V.immuno["death"]: float

    - Vaccination modifiers V.vaccine: Dict[str, float]
        Infection rate modifier V.vaccine["infection"]: float
        Contraction rate modifier V.vaccine["contraction"]: float
        Recovery rate modifier V.vaccine["recovery"]: float
        Death rate modifier V.vaccine["death"]: float

    - Asymptomatic modifiers V.asymptomatic: Dict[str, float]
        Infection rate modifier V.asymptomatic["infection"]: float
        Contraction rate modifier V.asymptomatic["contraction"]: float
        Recovery rate modifier V.asymptomatic["recovery"]: float
        Death rate modifier V.asymptomatic["death"]: float

    - Incubation period V.incubation_period: int
    - Vaccine time V.vaccine_time: int
    - Vaccination exist function: V.vaccine_exist: Callable[[int], bool]
    """
    __slots__ = (
        'name',
        'recovery',
        'death',
        'incubation_period',
        'vaccine_time',
        'vaccine_exist',
        'infectious',
        'contract',
        'effectiveness',
        'asymptomatic',
        'immuno',
        'vaccine',
        'recovered'
    )
    def __init__(self, config = {}):
        
        self.configure(config)

    def configure(self, config = {}):
        self.name = config.get('name', "default_virus")
        self.recovery = config.get('recoveryOdds', 0.1)
        self.death = config.get('deathOdds', 0.01)
        self.incubation_period = config.get('incubation_period', 5)
        self.vaccine_time = config.get('vaccine_time', 10)
        self.vaccine_exist = config.get('vaccine_exist', lambda x: False)
        
        transmission = [
            config.get('infectious', [0.5]),
            config.get('contract', [0.5]),
            config.get('effectiveness', [0.5]),
        ]
        if len(set(map(len, transmission))) == 1:
            self.infectious = transmission[0]
            self.contract = transmission[1]
            self.effectiveness = transmission[2]
        else:
            self.infectious = [sum(transmission[0])/len(transmission[0])]
            self.contract = [sum(transmission[1])/len(transmission[1])]
            self.effectiveness = [sum(transmission[2])/len(transmission[2])]

        self.asymptomatic = {
            "infection": config.get('asymptomatic_infection', 0.75),
            "contraction": config.get('asymptomatic_contraction', 1),
            "recovery": config.get('asymptomatic_recovery', 2),
            "death": config.get('asymptomatic_death', 0.1)
        }
        self.immuno = {
            "infection": config.get('immuno_infection', 1.5),
            "contraction": config.get('immuno_contraction', 1),
            "recovery": config.get('immuno_recovery', 0.2),
            "death": config.get('immuno_death', 5)
        }
        self.vaccine = {
            "infection": config.get('vaccine_infection', 0.6),
            "contraction": config.get('vaccine_contraction', 0.5),
            "recovery": config.get('vaccine_recovery', 5),
            "death": config.get('vaccine_death', 0.1)
        }
        self.recovered = {
            "infection": config.get('recovered_infection', 1),
            "contraction": config.get('recovered_contraction',1),
            "recovery": config.get('recovered_recovery', 1.5),
            "death": config.get('recovered_death', .75)
        }

    def __str__(self, day=0):
        return (f"\nVirus: {self.name}\n"
                f"Recovery Odds per Day: {self.recovery * 100:.2f}%\n"
                f"Death Odds per Day: {self.death * 100:.2f}%\n"
                f"Incubation Period: {self.incubation_period} days\n"
                f"Vaccine Time: {self.vaccine_time} days\n"
                f"Vaccine Exists: {self.vaccine_exist(day)}\n"
                f"Infectiousness Odds: {self.infectious}\n"
                f"Contract Odds: {self.contract}\n"
                f"Mask Effectiveness: {self.effectiveness}\n\n"
                f"Immunocompromised Infection Odds: {self.immuno['infection'] * 100:.2f}%\n"
                f"Immunocompromised Contract Odds: {self.immuno['contraction'] * 100:.2f}%\n"
                f"Immunocompromised Recovery Odds: {self.immuno['recovery'] * 100:.2f}%\n"
                f"Immunocompromised Death Odds: {self.immuno['death'] * 100:.2f}%\n\n"
                f"Vaccinated Infection Odds: {self.vaccine['infection'] * 100:.2f}%\n"
                f"Vaccinated Contract Odds: {self.vaccine['contraction'] * 100:.2f}%\n"
                f"Vaccinated Recovery Odds: {self.vaccine['recovery'] * 100:.2f}%\n"
                f"Vaccinated Death Odds: {self.vaccine['death'] * 100:.2f}%\n\n"
                f"Recovered Infection Odds: {self.recovered['infection'] * 100:.2f}%\n"
                f"Recovered Contract Odds: {self.recovered['contraction'] * 100:.2f}%\n"
                f"Recovered Recovery Odds: {self.recovered['recovery'] * 100:.2f}%\n"
                f"Recovered Death Odds: {self.recovered['death'] * 100:.2f}%\n\n"
                f"Asymptomatic Infection Odds: {self.asymptomatic['infection'] * 100:.2f}%\n"
                f"Asymptomatic Contract Odds: {self.asymptomatic['contraction'] * 100:.2f}%\n"
                f"Asymptomatic Recovery Odds: {self.asymptomatic['recovery'] * 100:.2f}%\n"
                f"Asymptomatic Death Odds: {self.asymptomatic['death'] * 100:.2f}%\n")

class Person:
    '''
        Tags:
        - Mutually Exclusive Status Person.status: Literal['healthy', 'sick', 'infected', 'dead']:
          - 'Healthy': not infected, not sick, can get infected and vaccinated, and can make descisions on behavior
            - only affected by strongest government 
            - can mask, vaccinate, isolate but only based on global values

          - 'Infected': infected but not sick, can spread virus but not die, can make descisions on behavior
            - does not know they are infected, but can spread virus
            - only affected by strongest government measure
            - can mask, isolate, vaccinate but only based on global values

          - 'Sick': infected and sick, can spread virus and die, can make descisions on behavior but not as much
            - knows they are infected, can spread virus, and thus will isolate themselves if they want
            - affected by all government measures
            - Can mask, can isolate based on self, but cannot vaccinate

          - 'Dead': dead, cannot do anything, cannot be infected, cannot spread virus

        - Immunocompromised: Person.immunocompromised: bool
        - Recovered: Person.recovered: bool
        - Asymptomatic: Person.asymptomatic: bool, Mutually Exclusive with Immunocompromised
        - Vaccinated: Person.vaccinated: bool
        - Masked: Person.masked: bool
        - Isolated: Person.isolated: bool

        - Countdown for vaccine to take effect: Person.vaccine_time: int
        - Countdown for incubation period: Person.incubation_period: int
    '''
    __slots__ = ('status', 'immunocompromised', 'recovered', 'asymptomatic', 'vaccinated', 'masked', 'isolated', 'vaccine_time', 'incubation_period')

    def __init__(self, config = {}):
        self.status = config.get('status', 'healthy')
        self.immunocompromised = config.get('immunocompromised', False)
        self.recovered = config.get('recovered', False)
        self.asymptomatic = config.get('asymptomatic', False)
        self.vaccinated = config.get('vaccinated', False)
        self.masked = config.get('masked', False)
        self.isolated = config.get('isolated', False)
        self.vaccine_time = config.get('vaccine_time', 0)
        self.incubation_period = config.get('incubation_period', 0)

    def __str__(self) -> str:
        """Return a string representation of the Person's status and attributes."""
        return (
            f"Status: {self.status}\n"
            f"Immunocompromised: {self.immunocompromised}\n"
            f"Recovered: {self.recovered}\n"
            f"Asymptomatic: {self.asymptomatic}\n"
            f"Vaccinated: {self.vaccinated}\n"
            f"Masked: {self.masked}\n"
            f"Isolated: {self.isolated}\n"
            f"Vaccine Time: {self.vaccine_time}\n"
            f"Incubation Period: {self.incubation_period}"
        )


    def infect(self, incubation_period):
        self.status = 'infected'
        self.incubation_period = incubation_period
    
    def sicken(self):
        self.status = 'sick' if self.incubation_period == 1 else self.status
        self.incubation_period = max(0, self.incubation_period - 1)
    
    def vaccinate(self, vaccine_time):
        self.vaccine_time = vaccine_time if (self.vaccine_time == 0 and self.status != 'sick' and not self.vaccinated) else self.vaccine_time
        
    def activatevaccine(self):
        self.vaccinated = self.vaccinated or self.vaccine_time == 1 
        self.vaccine_time = max(0, self.vaccine_time - 1)

    def recover(self):
        self.status = 'healthy'
        self.recovered = True
        self.incubation_period = 0

    def mask(self):
        self.masked = True

    def unmask(self):
        self.masked = False

    def isolate(self):
        self.isolated = True

    def unisolate(self):
        self.isolated = False
    
    def die(self):
        self.status = 'dead'

class Population:
    '''
        Population will have the following components:
            - Days since start: Population.days: int
            - A list of people as an array: Population.pop: [Person] of len(Population.population)
            - number of initially infected: Population.initial_infected: int
            - odds of connection between 2 people: Population.connection_odds: float
            - odds of immunocompromised: Population.immune_odds: float
            - odds of initially vaccinated: Population.vaccinated_odds: float
            - odds of asymptomatic: Population.asymptomatic_odds: float
            - odds of initially and permanently masking: Population.mask_odds: float

            - Threshold to mask on own: Population.mask_threshold: float 
                - odds of fail: Population.mask_fail: float 
            - Threshold to isolate on own: Population.isolate_threshold: float
                - odds of fail: Population.isolate_fail: float
            - Threshold to vaccinate on own: Population.vaccinate_threshold: float
                - odds of fail: Population.vaccinate_fail: float

        '''
    
    __slots__ = (
        'days',
        'population',
        'initialpopulation',
        'initial_infected',
        'connection_odds',
        'isolation_connection_odds',
        'immuno_odds',
        'vaccinated_odds',
        'immunovacodds',
        'asymptomatic_odds',
        'mask_odds',
        'mask_threshold',
        'mask_floor',
        'mask_fail',
        'isolate_threshold',
        'isolate_floor',
        'isolate_fail',
        'vaccinate_threshold',
        'vaccinate_floor',
        'vaccinate_fail',
        'graph'
    )
    
    def __init__(self, config):
        self.days = 0
        self.population = config.get("Population", 0)
        self.initialpopulation = config.get("Population", 0)
        self.initial_infected = config.get('initial_infected', 0)
        
        odds_defaults = {
            'connection_odds': 0.1,
            'isolation_connection_odds': 0.1,
            'immuno_odds': 0.1,
            'vaccinated_odds': 0.1,
            'immunovacodds': 0.1,
            'asymptomatic_odds': 0.1,
            'mask_odds': 0.1,
            'mask_threshold': 0.1,
            'mask_floor': 0.1,
            'mask_fail': 0.1,
            'isolate_threshold': 0.1,
            'isolate_floor': 0.1,
            'isolate_fail': 0.1,
            'vaccinate_threshold': 0.1,
            'vaccinate_floor': 0.1,
            'vaccinate_fail': 0.1
        }
        for key, default in odds_defaults.items():
            setattr(self, key, config.get(key, default))

        # Efficiently create the graph
        print(f"Creating graph with {self.population} nodes and {self.connection_odds} connection odds with fast graph")
        self.graph = nx.fast_gnp_random_graph(self.population, self.connection_odds)
        print("Graph created, setting up population")
        self.set_up_pop()
    
    def set_up_pop(self):
        # Use dictionary comprehension to create the person dictionaries
        self.graph.add_nodes_from(
            ((node, {
                'person': Person({
                    'status': 'healthy',
                    'immunocompromised': random.random() < self.immuno_odds,
                    'asymptomatic': (random.random() < self.asymptomatic_odds) and not (random.random() < self.immuno_odds),
                    'vaccinated': random.random() < (self.vaccinated_odds if not (random.random() < self.immuno_odds) else self.immunovacodds * self.vaccinated_odds),
                    'masked': random.random() < self.mask_odds,
                    'recovered': False
                })
            }) for node in range(self.population))
        )

        # Use random.sample to select the initial infected nodes
        for node in random.sample(list(self.graph.nodes), self.initial_infected):
            self.graph.nodes[node]["person"].status = 'sick'

    def __str__(self) -> str:
        attrs = {
            "Day": self.days,
            "Initial Population": self.population,
            "Current Population": self.getpopulation(),
            "Infected": self.getinfected(),
            "Dead": self.getdead(),
            "Recovered": self.getrecovered(),
            "Vaccinated": self.getvaccinated(),
            "Immune": self.getimmunocompromised(),
            "Asymptomatic": self.getasymptomatic(),
            "Masked": self.getmasked(),
            "Isolated": self.getisolated()
        }
        return "\n".join(f"{key}: {value}" for key, value in attrs.items())


# Getters
    def getpopulation(self):
        return self.population
    
    def getinfected(self):
        return sum([1 for node in self.graph.nodes if self.graph.nodes[node]["person"].status == 'infected'])
    
    def getrecovered(self):
        return sum([1 for node in self.graph.nodes if self.graph.nodes[node]["person"].recovered])
    
    def getdead(self):
        return self.initialpopulation - self.population

    def gethealthy(self):
        return sum([1 for node in self.graph.nodes if self.graph.nodes[node]["person"].status == 'healthy'])
    
    def getvaccinated(self):
        return sum([1 for node in self.graph.nodes if self.graph.nodes[node]["person"].vaccinated]) 
    
    def getasymptomatic(self):
        return sum([1 for node in self.graph.nodes if self.graph.nodes[node]["person"].asymptomatic])

    def getimmunocompromised(self):
        return sum([1 for node in self.graph.nodes if (self.graph.nodes[node]["person"].immunocompromised and self.graph.nodes[node]["person"].status == 'healthy') ])  

    def getmasked(self):
        return sum([1 for node in self.graph.nodes if self.graph.nodes[node]["person"].masked]) 

    def getsick(self):
        return sum([1 for node in self.graph.nodes if self.graph.nodes[node]["person"].status == 'sick'])

    def getisolated(self):
        return sum([1 for node in self.graph.nodes if self.graph.nodes[node]["person"].isolated])

    def getnotfullyvaccinated(self):
        return sum([1 for node in self.graph.nodes if self.graph.nodes[node]["person"].vaccine_time > 1])

# Setters
    def vaccinatepopulation(self, vaccinatenum):
        #take random sample of population who's not vaccinated and vaccicnate them
        #if they are immunocompromised, use the immunocompromised vaccine odds to see it it works
        for node in random.sample(list(self.graph.nodes), vaccinatenum):
            person = self.graph.nodes[node]["person"]
            if person.immunocompromised:
                if random.random() < self.immunovacodds:
                    person.vaccinate()
            else:
                person.vaccinate()

    def maskpopulation(self, masknum):
        for node in random.sample(list(self.graph.nodes), masknum):
            person = self.graph.nodes[node]["person"]
            person.mask()

    def isolatepopulation(self, isolatenum):
        for node in random.sample(list(self.graph.nodes), isolatenum):
            person = self.graph.nodes[node]["person"]
            person.isolate()
    def killnode(self, node):
        person = self.graph.nodes[node]["person"]
        person.die()
        self.graph.remove_node(node)
        self.population -= 1   

    def vacnode(self, node):
        person = self.graph.nodes[node]["person"]
        if (not person.immunocompromised or random.random() < self.immunovacodds):
            person.vaccinate()

class Government:
    ''' 
    Government will have the following components:
        Thresholds for public health measures:
        - Mask mandate: Government.mask_threshold: float
        - Quarantine: Government.quarantine_threshold: float
        - Total lockdown: Government.lockdown_threshold: float
        - Vaccination campaign: Government.vaccination_threshold: float

        Values for public health measures:
        - Mask wearing rate: Government.mask_rate: float
        - Quarantine rate: Government.quarantine_rate: float
        - Lockdown rate: Government.lockdown_rate: float
        - Vaccination rate: Government.vaccination_rate: float

        Vaccination campaign:
            - Vaccination rate: Government.vaccination_campaign: Callable[[int], float]
                Each day, the government will vaccinate a number of people based on the function
                - 0: no vaccinations
                - 1: 1 vaccination per day
                - lambda x(day): day; x vaccinations per day

        
    '''
    __slot__ = ('vaccinate_threshold', 'vaccinate_floor', 'vaccinate_amount', 'vaccinate_fail', 
                'mask_threshold', 'mask_floor', 'mask_amount', 'mask_fail',
                'isolate_threshold', 'isolate_floor', 'isolate_amount', 'isolate_fail',
                'vaccine_mandate', 'mask_mandate', 'isolate_mandate')
    
    def __init__(self, config):
        self.vaccinate_threshold = config.get('vaccinate_threshold', 0.1)
        self.vaccinate_floor = config.get('vaccinate_floor', 0.1)
        self.vaccinate_amount = config.get('vaccinate_amount', 0.1)
        self.vaccinate_fail = config.get('vaccinate_fail', 0.1)
        
        self.mask_threshold = config.get('mask_threshold', 0.1)
        self.mask_floor = config.get('mask_floor', 0.1)
        self.mask_amount = config.get('mask_amount', 0.1)
        self.mask_fail = config.get('mask_fail', 0.1)

        self.isolate_threshold = config.get('isolate_threshold', 0.1)
        self.isolate_floor = config.get('isolate_floor', 0.1)
        self.isolate_amount = config.get('isolate_amount', 0.1)
        self.isolate_fail = config.get('isolate_fail', 0.1)
        self.sick_isolate_fail = config.get('sick_isolate_fail', 0.1)

        self.vaccine_mandate = False
        self.mask_mandate = False
        self.isolate_mandate = False
        
        
    def __str__(self):
        s = "Government:\n"
        s += f"  vaccinate_threshold: {self.vaccinate_threshold*100:.2f}% to activate mandate\n"
        s += f"  vaccinate_floor: {self.vaccinate_floor*100:.2f}% to deactivate mandate\n"
        s += f"  vaccinate_amount: {self.vaccinate_amount*100:.2f}%\n\n"    
        s += f"  mask_threshold: {self.mask_threshold*100:.2f}% to activate mandate\n"
        s += f"  mask_floor: {self.mask_floor*100:.2f}% to deactivate mandate\n"    
        s += f"  mask_amount: {self.mask_amount*100:.2f}%\n\n"
        s += f"  isolate_threshold: {self.isolate_threshold*100:.2f}% to activate mandate\n"
        s += f"  isolate_floor: {self.isolate_floor*100:.2f}% to deactivate mandate\n"
        s += f"  isolate_amount: {self.isolate_amount*100:.2f}%\n\n"
        return s
        
class VirusSimulation():
    __slots__ = ("virus","population","government")
    
    def __init__(self, config, preinstalled = False):
        if preinstalled:
            self.virus: Virus = config[0]
            self.population: Population = config[1]
            self.government: Government = config[2]
        else:
            self.virus = Virus(config.get("virus",{}))
            self.population = Population(config.get("population",{}))
            self.government = Government(config.get("government",{}))
            
            
    
    def step(self, debug = False):
        virus = self.virus
        population = self.population
        government = self.government
        '''
        Run a single step of the simulation.
        start:

        Iterate population.days +=1

        if population.getinfected() > 0:
        
        start iterating through population:
        for each person:
                
            if no mask mandate (government.mask_mandate == False):
                if population.getinfected()/population.getpopulation() > self.mask_threshold:
                    for that person: (1-self.mask_fail) chance to use person.mask(), (1-self.mask_fail/3) chance instead if status is sick)
                if population.getinfected()/population.getpopulation() < self.mask_floor:
                    for that person: self.mask_fail chance to use person.unmask(), self.mask_fail/3 chance instead if status is sick
            else:
                if population.getmasked()/population.getpopulation() < government.mask_amount:
                    90% chance to use person.mask(), 99% chance instead if status is sick

            if no isolate mandate (government.isolate_mandate == False):
                if population.getinfected()/population.getpopulation() > self.isolate_threshold:
                    for that person: (1-self.isolate_fail) chance to use person.isolate(), (1-self.isolate_floor/3) chance instead if status is sick
                if population.getinfected()/population.getpopulation() < self.isolate_floor:
                    for that person: self.isolate_floor chance to use person.unisolate(), self.isolate_floor/3 chance instead if status is sick
            else:
                if population.getisolated()/population.getpopulation() < government.isolate_amount:
                    40% chance to use person.isolate(), 95% chance instead if status is sick

            if no vaccine mandate (government.vaccine_mandate == False):
                if population.getinfected()/population.getpopulation() > self.vaccinate_threshold:
                    for that person: (1-self.vaccinate_fail) chance to use population.vacnode() if not already vaccinated and vaccine_time == 0
            else:
                if population.getvaccinated()/population.getpopulation() < government.vaccinate_amount:
                    51% chance to use population.vacnode()
        
            
            Next we start checking for infections:
            if  person.status == 'sick' or (person.status == 'infected' and incubation_time < 3):
                for that person p1:
                Check for masking, isolation, and vaccination

                for each healthy neighbor p2:
                    Chance to connect = (population.isolation_connections_odds if p1.isolated else 1) * (population.isolation_connections_odds if p2.isolated else 1)
                    Chance to break through recovery immunity = (virus.recovery["infection"] if p1.recovered else 1) * (virus.recovery["contraction"] if p2.recovered else 1)
                    Chance to break through vaccine immunity = (virus.vaccine["infection"] if p1.asymptomatic else 1) * (virus.vaccine["contraction"] if p2.asymptomatic else 1)
                    increase odds of infection to immunocompromised people = (virus.immuno["infection"] if p1.immunocompromised else 1) * (virus.immuno["contraction"] if p2.immunocompromised else 1)
                    Chance to break through asymptomatic immunity = (virus.asymptomatic["infection"] if p1.asymptomatic else 1) * (virus.asymptomatic["contraction"] if p2.asymptomatic else 1)
                    Let i be random index of self.transmission[0] 
                    Chance to break through masking = (virus.infectious[i] if p1.masked else 1) * (virus.contract[i] if p2.masked else 1)

                    Odds of infection thus is:
                        Chance to connect * Chance to break through recovery immunity * Chance to break through vaccine immunity * increase odds of infection to immunocompromised people * Chance to break through asymptomatic immunity * Chance to break through masking

                    if random.random() < Odds of infection:
                        p2.infect()
            
                if sick:
                    if random.random() < self.virus.death:
                        population.killnode(person)
                    else if random.random() < self.virus.recovery:
                        person.recover()
                
                if infected:
                    person.sicken()  
            else if person.status == 'infected':
                person.sicken()'''
        vaccine_exists = virus.vaccine_exist(population.days)
        infected_percent = (population.getinfected()+population.getsick())/population.getpopulation()
        total_virus = population.getinfected() + population.getsick()
        masked_percent = population.getmasked()/population.getpopulation()
        isolated_percent = population.getisolated()/population.getpopulation()
        vaccinated_percent = population.getvaccinated()/population.getpopulation()
        mask_odds = 1 - population.mask_fail
        isolate_odds = 1 - population.isolate_fail
        vaccinate_odds = 1 - population.vaccinate_fail
        population.days += 1
        deadnodes = set()
        infectnodes = set()

        def person_step(p1):
            person: Person = population.graph.nodes[p1]["person"]
            person.activatevaccine()
                
            if government.mask_mandate:
                if person.status == 'sick' or masked_percent < government.mask_amount:
                    mask_chance = (1-government.mask_fail) if person.status != 'sick' else (1-government.mask_fail/10)
                    if random.random() < mask_chance:
                        person.mask()
            else:
                if infected_percent > population.mask_threshold:
                    mask_chance = mask_odds if person.status != 'sick' else (1-(population.mask_fail/3))
                    if random.random() < mask_chance:
                        person.mask()
                elif infected_percent < population.mask_floor:
                    unmask_chance = population.mask_fail if person.status != 'sick' else population.mask_fail/3
                    if random.random() < unmask_chance:
                        person.unmask()

            if government.isolate_mandate:
                if person.status == 'sick' or isolated_percent < government.isolate_amount:
                    isolate_chance = (1-government.isolate_fail) if person.status != 'sick' else (1-government.sick_isolate_fail)
                    if random.random() < isolate_chance:
                        person.isolate()
            else:
                if person.status == 'sick' or infected_percent > population.isolate_threshold:
                    isolate_chance = isolate_odds if person.status != 'sick' else (1-(population.isolate_fail/3))
                    if random.random() < isolate_chance:
                        person.isolate()
                elif infected_percent < population.isolate_floor:
                    unisolate_chance = population.isolate_fail if person.status != 'sick' else population.isolate_fail/3
                    if random.random() < unisolate_chance:
                        person.unisolate()
            
            if vaccine_exists:
                if government.vaccine_mandate:
                    if vaccinated_percent < government.vaccinate_amount:
                        if random.random() < (1-government.vaccinate_fail):
                            person.vaccinate(virus.vaccine_time)
                else:
                    if infected_percent > population.vaccinate_threshold:
                        if random.random() < vaccinate_odds:
                            person.vaccinate(virus.vaccine_time)

            # check for infections:
            if person.status == 'sick' or (person.status == 'infected' and person.incubation_period < 3):
                for p2 in population.graph.neighbors(p1):
                    neighbor = population.graph.nodes[p2]["person"]
                    i = random.randint(0, len(virus.infectious) - 1)
                    if neighbor.status == 'healthy' and random.random() < (population.isolation_connection_odds if person.isolated or neighbor.isolated else 1):
                        if random.random() < (virus.infectious[i]) * (virus.contract[i]) * (1 - virus.immuno['infection'] if person.immunocompromised else 1) * (1 - virus.immuno['contraction'] if neighbor.immunocompromised else 1):
                            if random.random() < (1 - virus.vaccine['infection'] if person.vaccinated else 1) * (1 - virus.vaccine['contraction'] if neighbor.vaccinated else 1):
                                if random.random() < (1- virus.effectiveness[i] if person.masked else 1) * (1 - virus.effectiveness[i] if neighbor.masked else 1):
                                    if random.random() < (1 - virus.recovered['infection'] if person.recovered else 1) * (1 - virus.recovered['contraction'] if neighbor.recovered else 1):
                                        if random.random() < (1 - virus.asymptomatic['infection'] if person.asymptomatic else 1) * (1 - virus.asymptomatic['contraction'] if neighbor.asymptomatic else 1):
                                            infectnodes.add(p2)

            if person.status == 'sick':
                if random.random() < virus.death * (virus.asymptomatic['death'] if person.asymptomatic else 1) * (virus.immuno['death'] if person.immunocompromised else 1) * (virus.vaccine['death'] if person.vaccinated else 1) * (virus.recovered['death'] if person.recovered else 1):
                    deadnodes.add(p1)
                elif random.random() < virus.recovery * (virus.asymptomatic['recovery'] if person.asymptomatic else 1) * (virus.immuno['recovery'] if person.immunocompromised else 1) * (virus.vaccine['recovery'] if person.vaccinated else 1) * (virus.recovered['recovery'] if person.recovered else 1):
                    person.recover()

            if person.status == 'infected':
                person.sicken()
                if person.vaccinated and (random.random() < virus.vaccine['recovery']):
                    person.incubation_period = 0
                    person.recover()     
        if total_virus > 0:
            k : int = 0
            start_time = time.time()
            for p1 in population.graph.nodes:
                if debug:
                    k+=1
                    status = population.graph.nodes[p1]["person"].status
                    t= time.time() - start_time
                    pps = str(round(((k/(t))), 2) if t != 0 else "∞") 
                    print(f"\r {k}{' ' * (5-len(str(k)))} out of {len(population.graph.nodes)} | status: {status}{' ' * (8-len((status)))} | people/s: {pps}{' ' * (10-len(pps))}", end='')
                person_step(p1)
                
                
            infected_percent = (population.getinfected()+population.getsick()) / population.getpopulation()
            dead_percent = population.getdead() / population.getpopulation()
            
            hit_threshold = lambda x : (infected_percent > x) or (dead_percent/2 > x)
            hit_floor = lambda x : (infected_percent < x) and not hit_threshold(x)
            multiplex = lambda p,q,r : (not r and (p or q)) or (r and (p and q))  # (NOT R AND (P OR Q)) OR (R AND (P AND Q))
                
            government.vaccine_mandate = multiplex(government.vaccine_mandate, hit_threshold(government.vaccinate_threshold), hit_floor(government.vaccinate_floor))
            government.mask_mandate = multiplex(government.mask_mandate, hit_threshold(government.mask_threshold), hit_floor(government.mask_floor))
            government.isolate_mandate = multiplex(government.isolate_mandate, hit_threshold(government.isolate_threshold), hit_floor(government.isolate_floor))  

            #remove dead people
            for dead in deadnodes:
                population.killnode(dead)
            for infected in infectnodes:
                population.graph.nodes[infected]["person"].infect(virus.incubation_period)

            if debug: 
                os.system('cls' if os.name == 'nt' else 'clear')
                print(self)
            return (population.getsick()+population.getinfected())   
          
    def __str__(self):
        s = f"Name of virus: {self.virus.name}\n"
        s += f"Day {self.population.days}:\n"
        s += f"  healthy: {self.population.gethealthy()} ({self.population.gethealthy()/self.population.initialpopulation:.2%} of original population)\n"
        s += f"  infected: {self.population.getinfected()} ({self.population.getinfected()/self.population.initialpopulation:.2%} of original population)\n"
        s += f"  sick: {self.population.getsick()} ({self.population.getsick()/self.population.initialpopulation:.2%} of original population)\n"
        s += f"  recovered: {self.population.getrecovered()} ({self.population.getrecovered()/self.population.initialpopulation:.2%} of original population)\n"
        s += f"  untouched: {self.population.getpopulation() - self.population.getrecovered() - self.population.getinfected()} ({(self.population.getpopulation() - self.population.getrecovered()- self.population.getinfected())/self.population.initialpopulation:.2%} of original population)\n"
        s += f"  dead: {self.population.getdead()} ({self.population.getdead()/self.population.initialpopulation:.2%} of original population)\n\n"

        s += f"  notfullyvaccinated: {self.population.getnotfullyvaccinated()} ({self.population.getnotfullyvaccinated()/self.population.population:.2%} of current population)\n"
        s += f"  vaccinated: {self.population.getvaccinated()} ({self.population.getvaccinated()/self.population.population:.2%} of current population)\n"
        s += f"  immunocompromised: {self.population.getimmunocompromised()} ({self.population.getimmunocompromised()/self.population.population:.2%} of current population)\n\n"
        s += f"  asymptomatic: {self.population.getasymptomatic()} ({self.population.getasymptomatic()/self.population.population:.2%} of current population)\n"    
        s += f"  isolated: {self.population.getisolated()} ({self.population.getisolated()/self.population.population:.2%} of current population)\n"
        s += f"  masked: {self.population.getmasked()} ({self.population.getmasked()/self.population.population:.2%} of current population)\n\n"

        s += f"  vaccine_mandate: {self.government.vaccine_mandate}\n"
        s += f"     mandate met: {(self.population.getmasked()/self.population.getpopulation()) > self.government.mask_threshold}\n"
        s += f"  mask_mandate: {self.government.mask_mandate}\n"
        s += f"     mandate met: {(self.population.getmasked()/self.population.getpopulation()) > self.government.isolate_threshold}\n"
        s += f"  isolate_mandate: {self.government.isolate_mandate}\n"
        s += f"     mandate met: {(self.population.getisolated()/self.population.getpopulation()) > self.government.vaccinate_threshold}\n"

        return s

    def get_simulation_info(self):
        return {
            "Day": self.population.days,
            "original_healthy": self.population.initialpopulation,
            "end_healthy": self.population.gethealthy(),
            "original_infected": self.population.initial_infected,
            "end_infected": self.population.getinfected(),
            "sick": self.population.getsick(),
            "recovered": self.population.getrecovered(),
            "untouched": self.population.getpopulation() - self.population.getrecovered() - self.population.getinfected(),
            "dead": self.population.getdead(),
            
            "percentage_died": self.population.getdead() / self.population.initialpopulation,
            "percentage_untouched": (self.population.getpopulation() - self.population.getrecovered() - self.population.getinfected()) / self.population.initialpopulation,
            
            "notfullyvaccinated": self.population.getnotfullyvaccinated(),
            
            "original_vaccinated": self.population.initialpopulation * self.population.vaccinated_odds,
            "vaccinated": self.population.getvaccinated(),
            "end_vaccinated_percentage": self.population.getvaccinated() / self.population.initialpopulation,
            
            "original_immunocompromised": self.population.initialpopulation * self.population.immuno_odds,
            "immunocompromised": self.population.getimmunocompromised(),
            "end_immunocompromised_percentage": self.population.getimmunocompromised() / self.population.initialpopulation,
            
            "original_asymptomatic": self.population.initialpopulation * self.population.asymptomatic_odds,
            "asymptomatic": self.population.getasymptomatic(),
            "end_asymptomatic_percentage": self.population.getasymptomatic() / self.population.initialpopulation,
            
            "isolated": self.population.getisolated(),
            "end_isolated_percentage": self.population.getisolated() / self.population.initialpopulation,
            
            "original_masked": self.population.initialpopulation * self.population.mask_odds,
            "masked": self.population.getmasked(),
            "end_masked_percentage": self.population.getmasked() / self.population.initialpopulation,
            
            
        }
    
    def getplotinfo(self):
        return {
            "healthy": self.population.getpopulation() - self.population.getinfected(),
            "infected": self.population.getinfected(),
            "recovered": self.population.getrecovered(),
            "dead": self.population.getdead(),
            "vaccinated": self.population.getvaccinated(),
            "isolated": self.population.getisolated(),
            "masked": self.population.getmasked(),
            "immunocompromised": self.population.getimmunocompromised(),
            "asymptomatic": self.population.getasymptomatic()}

    def bigsim(self, max_steps = 1000, debug = False):
        if debug:
            print(self)
        while self.step(debug) and self.population.days<max_steps:
            if not debug:
                print(f"Day: {self.population.days}{6-str(self.population.days)}", end="\r")
        return True


if __name__ == "__main__":
    virus: Virus = Virus()
    person = Person()
    print("Healthy Person")
    print(person)
    print()
    person.vaccinate(virus.vaccine_time)
    print("Vaccinated Person, Not fully")
    print(person)
    print()
    print("Infected not sick")
    person.infect(20)
    print(person)
    print()
    
    while person.vaccine_time>0:
        person.activatevaccine()
        person.vaccinate(virus.vaccine_time)
        print(person)
        print()
    
    while person.incubation_period>0:
        person.sicken()
        print(person)
        print()
 