import pandas as pd
import networkx as nx
from bokeh.io import curdoc
from bokeh.layouts import column, row
from bokeh.models import FileInput, Tabs,TabPanel,Label,Slider,NumericInput
from bokeh.plotting import figure,from_networkx
from bokeh.palettes import Category20_20
import random 
from genetic import Chromosome , Genetic

# Controllers

root_page = curdoc()
root_page.title = "TSP Problem"

file_input = FileInput()
file_input.accept='.csv'
file_input.multiple = False

graph_box = row(figure())

mutation_rate_slider = Slider(start=0, end=1, value=0.01, step=0.01, title="Mutation Rate")
population_numeric_input = NumericInput(value=50, low=1, high=1000, title="Population Size:")
genetic_tab_column = column(row(mutation_rate_slider,population_numeric_input),figure())

genetic_algo_tab = TabPanel(title="Genetic Algorithm", child=genetic_tab_column)
pso_algo_tab = TabPanel(title="PSO Algorithm", child=figure())
ant_colony_tab = TabPanel(title="Ant Colony", child=figure())

algorithm_tabs = Tabs(tabs=[genetic_algo_tab, pso_algo_tab, ant_colony_tab])

root_page.add_root(column(file_input,row(graph_box, algorithm_tabs)))

G = None

#Algorithms
def fitness_function(gene):
    global G
    fitness = 0
    for i,v in enumerate(gene):
        try:
            if i == len(gene)-1:
                fitness+= G.adj[v][gene[0]]['w']
            else:
                fitness+= G.adj[v][gene[i+1]]['w']
        except:
            try:
                fitness += 1000000
            except:
                pass
    return fitness

def random_gene_maker():
    return random.sample(list(G.nodes()),k=len(G))

# genetic = Genetic(fitness_function=fitness_function,population_size=100,
#         mutation_rate=0.01,random_gen_maker=random_gene_maker,
#         crossover_type={'type':'pmx'},mutation_type={'type':'scrumble'},isbest_min=True,
#         selection_function=selection_function,replacement_function=replacement_function,
#         selection_size=50)

#Events:
def handle_file_upload(attr, old, new):
    global G
    selected_file = new
    if selected_file:
        df = pd.read_csv(selected_file, names=['n1', 'n2', 'w'])
        # Assuming the CSV file has columns 'n1', 'n2', and 'w'
        G = nx.from_pandas_edgelist(df, 'n1', 'n2', edge_attr='w', create_using=nx.Graph())
        # Extract edge weights as a list
        edge_weights = df['w'].tolist()
        
        # Plot the graph
        plot = figure(title="Map",x_range=(-1.1, 1.1), y_range=(-1.1, 1.1),
            x_axis_location=None, y_axis_location=None,
            tooltips="index: @index")
        plot.grid.grid_line_color = None

        
        positions = nx.spring_layout(G,k=1.8)
        graph = from_networkx(G, positions, scale=1.8, center=(0,0))
        plot.renderers.append(graph)

        # Add some new columns to the node renderer data source
        graph.node_renderer.data_source.data['index'] = list(G.nodes())
        color=[]
        if not len(G)>20:
            color = random.sample(Category20_20,k=len(G))
        else :
            for i in range(len(G)//20):
                color += Category20_20
            color = random.sample(Category20_20,k=(len(G)-1)%20)
        graph.node_renderer.data_source.data['colors'] = color

        graph.node_renderer.glyph.update(size=20, fill_color="colors")

        
        for (n1, n2), weight in zip(G.edges(), edge_weights):
            midpoint = (positions[n1][0] + positions[n2][0]) / 2, (positions[n1][1] + positions[n2][1]) / 2
            label = Label(x=midpoint[0], y=midpoint[1], text=f'{weight}', text_font_size='14pt')
            plot.add_layout(label)
        
        # Update the algorithm tabs with the new graph
        graph_box.children[0] = plot

file_input.on_change("filename", handle_file_upload)