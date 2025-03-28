import networkx as nx
import random
from typing import List, Dict, Tuple, Union, Callable


'''
things to add:

- Complex virus: 

    Virus now has an incubation period, and can be spread during that period with a lower rate of transmission (Person counts as "infected" rather than sick)
    - if not vaccinated, person will become sick after incubation period and only then can start recovery
    - if vaccinated, person can start recovering during incubation period
    - Cannot die during incubation period, but can spread

    No mutations will be done

    
- Different Transmission dynamics:

    instead of just 2 values Pu, Pc; they are arrays that act in pairs,
    This also means that the masking effect can be an array

    To trigger:

    - Before running masking calc roll random index of Pu, and use that index for all calculations,
        this simulating interaction through coughing, sneezing, direct contact, etc.
        and Masking effects include wearing masks, washing hands, elbow coughing, etc.
    - So odds of catching infection from sick person on a given day is: 
        Pu[i] * Pc[i] *(1-(mask_effectiveness[i] if masked else 0) ) * (1-(mask_effectiveness[i] if masked else 0))


- Complex Vaccinations: Pv has multiple components now:

    2 types of vaccines:
        - Long term immunity: fewer immunocompromised people can get this vaccine but it is more effective in the long run
        - Short term immunity: more people can get this vaccine but it is less effective in the long run, wearing out after a few months
        - Time for vaccine to take effect: Only after this time will a person be fully vaccinated and thus have the vaccination effects

        what is key is that the size of this sim is small enough that the only part that matters is how many people can get the vaccine, not the duration of effect

    
- Dynamic Outbreak:
    Simulate public reaction by giving people the ability to change their behavior based on the current situation
    - People can choose to wear masks or not based on the overall percentage of sick rate
    - People can choose to isolate themselves based on the overall percentage of sick rate, and also while they are sick (both result in 5% contact rate)
    - People can choose to get vaccinated based on the overall percentage of sick rate if they are healthy


- Public Health Measures:
    Upon a given threshold of infections, trigger a public health measure:
    - Mask mandate: all people must wear masks (resulting in 90% mask wearing rate)
    - Quarantine: all people must isolate themselves when sick (resulting in 5% contact rate for sick people guaranteed when incubation ends, 65% chance each day to isolated while in incubation)
    - Total lockdown: all people must isolate themselves (resulting in 5% contact rate for sick people guaranteed when incubation ends, 10% contact rate for healthy people)
    - Vaccination campaign: all people must get vaccinated (resulting in 90% vaccination rate for short term vaccine, 60% for long term vaccine if vaccine exists)


'''
'''
This will require an overhaul of how the simulation works, now actually having a Person Class that will be at each node.

VirusSim will have the following components:
    - A Virus that will infect others:
    - A Population to be infected:
    - A Government that will implement public health measures based on the current situation
'''


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
            config.get('infectious'),
            config.get('contract'),
            config.get('effectiveness'),
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

    def __init__(self, config):
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
        self.incubation_period -= 1 if self.incubation_period > 0 else 0
    
    def vaccinate(self, vaccine_time):
        self.vaccine_time = vaccine_time if self.vaccine_time == 0 and self.status != 'sick' else 0
        
    def activatevaccine(self):
        self.vaccinated = self.vaccine_time == 1
        self.vaccine_time -= 1 if self.vaccine_time > 0 else 0

    def recover(self):
        self.status = 'healthy'
        self.recovered = True

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
    def __init__(self, config):
        self.days = 0
        self.population = config.get("Population", 0)
        self.initialpopulation = config.get("Population", 0)
        self.initial_infected = config.get('initial_infected', 0)
        
        # Use dictionary unpacking for odds to reduce repetitive code
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
            'vaccinate_fail': 0.1
        }
        
        # Update self attributes using the config values or defaults
        self.__dict__.update({key: config.get(key, default) for key, default in odds_defaults.items()})

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
                    'vaccinated': random.random() < (self.vaccinated_odds if not (random.random() < self.immuno_odds) else self.immunovacodds),
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
        return sum([1 for node in self.graph.nodes if self.graph.nodes[node]["person"].immunocompromised])  

    def getmasked(self):
        return sum([1 for node in self.graph.nodes if self.graph.nodes[node]["person"].masked]) 

    def getsick(self):
        return sum([1 for node in self.graph.nodes if self.graph.nodes[node]["person"].status == 'sick'])

    def getisolated(self):
        return sum([1 for node in self.graph.nodes if self.graph.nodes[node]["person"].isolated])

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

    def __init__(self, config):
        self.vaccinate_threshold = config.get('vaccinate_threshold', 0.1)
        self.vaccinate_floor = config.get('vaccinate_floor', 0.1)
        self.vaccinate_amount = config.get('vaccinate_amount', 0.1)

        self.mask_threshold = config.get('mask_threshold', 0.1)
        self.mask_floor = config.get('mask_floor', 0.1)
        self.mask_amount = config.get('mask_amount', 0.1)

        self.isolate_threshold = config.get('isolate_threshold', 0.1)
        self.isolate_floor = config.get('isolate_floor', 0.1)
        self.isolate_amount = config.get('isolate_amount', 0.1)

        self.vaccine_mandate = False
        self.mask_mandate = False
        self.isolate_mandate = False
        
class VirusSimulation():
    def __init__(self, config):
        self.virus = Virus(config["virus"])
        self.population = Population(config["population"])
        self.government = Government(config["government"])
    
    def step(self):
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
        infected_percent = (population.getinfected()+population.getsick())/population.getpopulation()
        total_virus = population.getinfected() + population.getsick()
        mask_fail_value = 1 - population.mask_fail
        isolate_fail_value = 1 - population.isolate_fail
        vaccinate_fail_value = 1 - population.vaccinate_fail
        
        population.days += 1
        
        deadnodes = []
        if total_virus > 0:
            k = 0
            for p1 in population.graph.nodes:
                print(k:=k+1, "out of", len(population.graph.nodes),f"status: {population.graph.nodes[p1]['person'].status}", end='\r')
                person = population.graph.nodes[p1]["person"]
                
                masked_percent = population.getmasked()/population.getpopulation()
                isolated_percent = population.getisolated()/population.getpopulation()
                vaccinated_percent = population.getvaccinated()/population.getpopulation()


                if government.mask_mandate:
                    if masked_percent < government.mask_amount:
                        mask_chance = 0.9 if person.status != 'sick' else 0.99
                        if random.random() < mask_chance:
                            person.mask()
                else:
                    if infected_percent > population.mask_threshold:
                        mask_chance = mask_fail_value if person.status != 'sick' else mask_fail_value/3
                        if random.random() < mask_chance:
                            person.mask()
                    elif infected_percent < population.mask_floor:
                        unmask_chance = population.mask_fail if person.status != 'sick' else population.mask_fail/3
                        if random.random() < unmask_chance:
                            person.unmask()

                if government.isolate_mandate:
                    if isolated_percent < government.isolate_amount:
                        isolate_chance = 0.4 if person.status != 'sick' else 0.95
                        if random.random() < isolate_chance:
                            person.isolate()
                else:
                    if infected_percent > population.isolate_threshold:
                        isolate_chance = isolate_fail_value if person.status != 'sick' else isolate_fail_value/3
                        if random.random() < isolate_chance:
                            person.isolate()
                    elif infected_percent < population.isolate_floor:
                        unisolate_chance = population.isolate_fail if person.status != 'sick' else population.isolate_fail/3
                        if random.random() < unisolate_chance:
                            person.unisolate()

                if government.vaccine_mandate:
                    if vaccinated_percent < government.vaccinate_amount:
                        if random.random() < 0.51:
                            person.vaccinate(virus.vaccine_time)
                else:
                    if infected_percent > population.vaccinate_threshold:
                        if random.random() < vaccinate_fail_value:
                            person.vaccinate(virus.vaccine_time)

                # check for infections:
                '''
                if person.status == 'sick' or (person.status == 'infected' and person.incubation_period < 3):
                    for p2 in population.graph.neighbors(p1):
                        neighbor = population.graph.nodes[p2]["person"]
                        if neighbor.status == 'healthy' and random.random() < (population.connection_odds if person.isolated else 1) * (population.connection_odds if neighbor.isolated else 1):


                            recovery_chance = (1 - virus.recovered['infection'] if person.recovered else 1) * (1 - virus.recovered['contraction'] if neighbor.recovered else 1)
                            vaccine_chance = (1 - virus.vaccine['infection'] if person.vaccinated else 1) * (1 - virus.vaccine['contraction'] if neighbor.vaccinated else 1)
                            immuno_chance = (1 - virus.immuno['infection'] if person.immunocompromised else 1) * (1 - virus.immuno['contraction'] if neighbor.immunocompromised else 1)
                            asymptomatic_chance = (1 - virus.asymptomatic['infection'] if person.asymptomatic else 1) * (1 - virus.asymptomatic['contraction'] if neighbor.asymptomatic else 1)
                            i = random.randint(0, len(virus.infectious) - 1)
                            mask_chance = (1 - virus.effectiveness[i] if person.masked else 1) * (1 - virus.effectiveness[i] if neighbor.masked else 1)
                            normal_odds = (virus.infectious[i] if person.masked else 1) * (virus.contract[i] if neighbor.masked else 1)             
                            if random.random() < (recovery_chance * vaccine_chance * immuno_chance * asymptomatic_chance * mask_chance * normal_odds):
                                neighbor.infect(virus.incubation_period)
            
                '''
                if person.status == 'sick' or (person.status == 'infected' and person.incubation_period < 3):
                    for p2 in population.graph.neighbors(p1):
                        neighbor = population.graph.nodes[p2]["person"]
                        i = random.randint(0, len(virus.infectious) - 1)
                        if neighbor.status == 'healthy' and random.random() < (population.connection_odds if person.isolated else 1) * (population.connection_odds if neighbor.isolated else 1):
                            if random.random() < (virus.infectious[i]) * (virus.contract[i]) * (1 - virus.immuno['infection'] if person.immunocompromised else 1) * (1 - virus.immuno['contraction'] if neighbor.immunocompromised else 1):
                                if random.random() < (1 - virus.vaccine['infection'] if person.vaccinated else 1) * (1 - virus.vaccine['contraction'] if neighbor.vaccinated else 1):
                                    if random.random() < (1- virus.effectiveness[i] if person.masked else 1) * (1 - virus.effectiveness[i] if neighbor.masked else 1):
                                        if random.random() < (1 - virus.recovered['infection'] if person.recovered else 1) * (1 - virus.recovered['contraction'] if neighbor.recovered else 1):
                                            if random.random() < (1 - virus.asymptomatic['infection'] if person.asymptomatic else 1) * (1 - virus.asymptomatic['contraction'] if neighbor.asymptomatic else 1):
                                                neighbor.infect(virus.incubation_period)



                if person.status == 'sick':
                    if random.random() < virus.death * (virus.asymptomatic['death'] if person.asymptomatic else 1) * (virus.immuno['death'] if person.immunocompromised else 1) * (virus.vaccine['death'] if person.vaccinated else 1) * (virus.recovered['death'] if person.recovered else 1):
                        deadnodes.append(p1)
                    elif random.random() < virus.recovery * (virus.asymptomatic['recovery'] if person.asymptomatic else 1) * (virus.immuno['recovery'] if person.immunocompromised else 1) * (virus.vaccine['recovery'] if person.vaccinated else 1) * (virus.recovered['recovery'] if person.recovered else 1):
                        person.recover()

                if person.status == 'infected':
                    person.sicken()
                    if person.vaccinated and (random.random() < virus.vaccine['recovery']):
                        person.incubation_period = 0
                        person.recover()
            infected_percent = population.getinfected() / population.getpopulation()
            dead_percent = population.getdead() / population.getpopulation()
            
            hit_threshold = lambda x : (infected_percent > x) or (dead_percent > x)
            hit_floor = lambda x : (infected_percent < x) and not hit_threshold(x)
            multiplex = lambda p,q,r : (not r and (p or q)) or (r and (p and q))  # (NOT R AND (P OR Q)) OR (R AND (P AND Q))
                
            government.vaccine_mandate = multiplex(government.vaccine_mandate, hit_threshold(government.vaccinate_threshold), hit_floor(government.vaccinate_floor))
            government.mask_mandate = multiplex(government.mask_mandate, hit_threshold(government.mask_threshold), hit_floor(government.mask_floor))
            government.isolate_mandate = multiplex(government.isolate_mandate, hit_threshold(government.isolate_threshold), hit_floor(government.isolate_floor))  

            #remove dead people
            for dead in deadnodes:
                population.graph.remove_node(dead)
            return (population.getsick()+population.getinfected())   
          
    def catchodds(self,person1:Person,person2:Person)->float:
        virus = self.virus
        recovery_chance = (1 - virus.recovered['infection'] if person1.recovered else 1) * (1 - virus.recovered['contraction'] if person2.recovered else 1)
        vaccine_chance = (1 - virus.vaccine['infection'] if person1.vaccinated else 1) * (1 - virus.vaccine['contraction'] if person2.vaccinated else 1)
        immuno_chance = (1 - virus.immuno['infection'] if person1.immunocompromised else 1) * (1 - virus.immuno['contraction'] if person2.immunocompromised else 1)
        asymptomatic_chance = (1 - virus.asymptomatic['infection'] if person1.asymptomatic else 1) * (1 - virus.asymptomatic['contraction'] if person2.asymptomatic else 1)
        i = random.randint(0, len(virus.infectious) - 1)
        mask_chance = (1 - virus.effectiveness[i] if person1.masked else 1) * (1 - virus.effectiveness[i] if person2.masked else 1)
        normal_odds = (virus.infectious[i]) * (virus.contract[i])             
        return recovery_chance * vaccine_chance * immuno_chance * asymptomatic_chance * mask_chance * normal_odds





    def __str__(self):
        s = f"Day {self.population.days}:\n"
        s += f"  healthy: {self.population.gethealthy()}\n"
        s += f"  sick: {self.population.getsick()}\n"
        s += f"  infected: {self.population.getinfected()}\n"
        s += f"  recovered: {self.population.getrecovered()}\n"
        s += f"  dead: {self.population.getdead()}\n\n"

        s += f"  vaccinated: {self.population.getvaccinated()}\n"
        s += f"  immunocompromised: {self.population.getimmunocompromised()}\n"
        s += f"  asymptomatic: {self.population.getasymptomatic()}\n"    
        s += f"  isolated: {self.population.getisolated()}\n"
        s += f"  masked: {self.population.getmasked()}\n\n"

        s += f"  vaccine_mandate: {self.government.vaccine_mandate}\n"
        s += f"  mask_mandate: {self.government.mask_mandate}\n"
        s += f"  isolate_mandate: {self.government.isolate_mandate}\n"

        



        return s

              
if __name__ == "__main__":

    test_virus_config = {
        "name": "default",
        "recoveryOdds": 0.1,
        "deathOdds": 0.01,
        "incubation_period": 5,
        "vaccine_time": 14,
        "vaccine_exist": lambda x: True,
        "infectious": [0.3, 0.2, 0.1],
        "contract": [0.9, 0.95, 0.1],
        "effectiveness": [0.7, 0.95, 0.1],

        "asymptomatic_infection": 1,
        "asymptomatic_contraction": 1,
        "asymptomatic_recovery": 0.1,
        "asymptomatic_death": 0.01,

        "immuno_infection": 1,
        "immuno_contraction": 1,
        "immuno_recovery": 0.1,
        "immuno_death": 0.01,

        "vaccine_infection": 1,
        "vaccine_contraction": 1,
        "vaccine_recovery": 0.1,
        "vaccine_death": 0.01,

        "recovered_infection": 1,
        "recovered_contraction": 1,
        "recovered_recovery": 0.1,
        "recovered_death": 0.1,
    }

    virus = Virus(test_virus_config)
    print(virus)




    test_population_config = {
        "Population": 50000,
        "initial_infected": 10,
        "connection_odds": 0.01,
        "isolation_connection_odds": 0.005,
        "immune_odds": 0.1,
        "vaccinated_odds": 0.1,
        "immunovacodds": 0.05,
        "asymptomatic_odds": 0.1,
        "mask_odds": 0.1,
        "mask_threshold": 0.1,
        "mask_floor": 0.05,
        "mask_fail": 0.1,
        "isolate_threshold": 0.1,
        "isolate_floor": 0.05,
        "isolate_fail": 0.1,
        "vaccinate_threshold": 0.1,
        "vaccinate_fail": 0.1,
    }

    test_government_config = {
        "vaccinate_threshold": 0.1,
        "vaccinate_floor": 0.05,
        "vaccinate_amount": 0.1,
        "mask_threshold": 0.1,
        "mask_floor": 0.05,
        "mask_amount": 0.1,
        "isolate_threshold": 0.1,
        "isolate_floor": 0.05,
        "isolate_amount": 0.1,
    }

    test_sim_config = {
        "virus": test_virus_config,
        "population": test_population_config,
        "government": test_government_config,
    }

    sim = VirusSimulation(test_sim_config)

    print(sim)

    while sim.step():
        print(sim)

    print(sim)


    '''
                if person.status == 'sick' or (person.status == 'infected' and person.incubation_period < 3):
                    for p2 in population.graph.neighbors(p1):
                        neighbor = population.graph.nodes[p2]["person"]
                        if neighbor.status == 'healthy' and random.random() < (population.connection_odds if person.isolated else 1) * (population.connection_odds if neighbor.isolated else 1):


                            recovery_chance = (1 - virus.recovered['infection'] if person.recovered else 1) * (1 - virus.recovered['contraction'] if neighbor.recovered else 1)
                            vaccine_chance = (1 - virus.vaccine['infection'] if person.vaccinated else 1) * (1 - virus.vaccine['contraction'] if neighbor.vaccinated else 1)
                            immuno_chance = (1 - virus.immuno['infection'] if person.immunocompromised else 1) * (1 - virus.immuno['contraction'] if neighbor.immunocompromised else 1)
                            asymptomatic_chance = (1 - virus.asymptomatic['infection'] if person.asymptomatic else 1) * (1 - virus.asymptomatic['contraction'] if neighbor.asymptomatic else 1)
                            i = random.randint(0, len(virus.infectious) - 1)
                            mask_chance = (1 - virus.effectiveness[i] if person.masked else 1) * (1 - virus.effectiveness[i] if neighbor.masked else 1)
                            normal_odds = (virus.infectious[i] if person.masked else 1) * (virus.contract[i] if neighbor.masked else 1)             
                            if random.random() < (recovery_chance * vaccine_chance * immuno_chance * asymptomatic_chance * mask_chance * normal_odds):
                                neighbor.infect(virus.incubation_period)
            
                '''