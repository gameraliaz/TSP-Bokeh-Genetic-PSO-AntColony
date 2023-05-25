import pandas as pd
import networkx as nx
from bokeh.io import curdoc
from bokeh.layouts import column, row
from bokeh.models import ColumnDataSource,ColorPicker,HoverTool,PreText,FileInput, Tabs,TabPanel,Label,Slider,NumericInput, Button, Select,RadioButtonGroup,AutocompleteInput
from bokeh.plotting import figure,from_networkx
from bokeh.palettes import Category20_20
import random 
from genetic import  Genetic

G = None
datachart = {}
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

# Controllers

root_page = curdoc()
root_page.title = "TSP Problem"

file_input = FileInput()
file_input.accept='.csv'
file_input.multiple = False

graph_box = row(figure())

# Genetic
Name_auto_complete_input = AutocompleteInput(title="Name:", completions=[])
Generation_numericalinput = NumericInput(value=50,low=1,high=1000,title="Number of Generation:")
row0 = row(Name_auto_complete_input,Generation_numericalinput)

population_numeric_input = NumericInput(value=100, low=1, high=1000, title="Population Size:")
selection_numeric_input = NumericInput(value=50, low=1, high=1000, title="Selection Size:")
row1 = row(population_numeric_input,selection_numeric_input)

mutation_rate_slider = Slider(start=0, end=1, value=0.01, step=0.01, title="Mutation Rate")
crossover_type_select = Select(title="Crossover function:", value="pmx", options=["pmx", "ox", "cx"])
mutation_type_select = Select(title="Mutation function:", value="swap", options=["swap", "insert", "inversion","scrumble"])
row2 = row(mutation_rate_slider,mutation_type_select,crossover_type_select)

selectionfunclable = PreText(text="Selection function:", width=200, height=10)
selection_label = ["random","best","roulette",'tournament','rank']
selection_type_select = RadioButtonGroup(labels=selection_label, active=0)
col1= column(selectionfunclable,selection_type_select)
replacementfunclable = PreText(text="Replacement function:", width=200, height=10)
replacement_label = ["new","best","best-half","new-best-old"]
replacement_type_select = RadioButtonGroup(labels=replacement_label, active=0)
col2= column(replacementfunclable,replacement_type_select)
row3 = row(col1,col2)

button = Button(label='start', button_type="primary")
colorpicker = ColorPicker(title="Line Color")
row4 = row(button,colorpicker)


genetic_figure=figure(title="Genetic Algorithm", x_axis_label="Generation", y_axis_label="Best Fitness")
genetic_figure.add_tools(HoverTool(tooltips="Generation: @Generation, Fitness: @Fitness", mode="vline"))
Output = PreText(text="", width=0, height=0)
row5_2=row(Output)

row5=row(genetic_figure)
def callback(b:Button):
    print("on start/stop")
    global datachart,Name_auto_complete_input,Generation_numericalinput
    Nameinput = Name_auto_complete_input.value_input
    GenerationMax = Generation_numericalinput.value
    if Nameinput in datachart.keys():
        if datachart[Nameinput]["IsEnabel"]:
            print("already running!")
        else:
            lineChart = None

            for i in genetic_figure.renderers:
                if i.name == Nameinput:
                    lineChart = i
            datachart[Nameinput]["IsEnabel"] = True
            algo = datachart[Nameinput]["algorithm"]
            
            if algo.generation < GenerationMax:
                for i in algo.Execute():
                    print(f"Generation : {algo.generation}\tFitness : {algo.best.fitness}")
                    datachart[Nameinput]["generation"].append(algo.generation)
                    datachart[Nameinput]["fitness"].append(algo.best.fitness)

                    lineChart.data_source.stream({"Generation":[algo.generation] , "Fitness":[algo.best.fitness]})
                    Output = PreText(text=f"Generation: {algo.generation}\nBest : \n\tGeneration: {algo.bestgen}\tFitness: {algo.best.fitness}\n\tGene: {algo.best.gene}", width=200, height=75)
                    row5_2.children[0]=Output
                    if algo.generation >= GenerationMax:
                        break
            datachart[Nameinput]["IsEnabel"] = False

    else:
        algo = Genetic(fitness_function,population_numeric_input.value,mutation_rate_slider.value
                            ,random_gene_maker,{'type':crossover_type_select.value},{'type':mutation_type_select.value},
                            True,selection_label[selection_type_select.active],
                            replacement_label[replacement_type_select.active],[selection_numeric_input.value,(population_numeric_input.value//selection_numeric_input.value)])
        datachart.update({Nameinput:{"algorithm":algo,"IsEnabel":True,"generation":[],"fitness":[]}})
        

        data = {'Generation': [],
                'Fitness': []}
        source = ColumnDataSource(data=data)

        line = genetic_figure.line(legend_label=Nameinput,
                            name=Nameinput,
                            color=colorpicker.color,
                            line_width=2,x="Generation",y="Fitness",source=source)
        genetic_figure.legend.click_policy="mute"
        Name_auto_complete_input.completions.append(Nameinput)

        if algo.generation < GenerationMax:
            for i in algo.Execute():
                print(f"Generation : {algo.generation}\tFitness : {algo.best.fitness}")
                datachart[Nameinput]["generation"].append(algo.generation)
                datachart[Nameinput]["fitness"].append(algo.best.fitness)
                line.data_source.stream({"Generation":[algo.generation] , "Fitness":[algo.best.fitness]})
                Output = PreText(text=f"Generation: {algo.generation}\nBest : \n\tGeneration: {algo.bestgen}\tFitness: {algo.best.fitness}\n\tGene: {algo.best.gene}", width=200, height=75)
                row5_2.children[0]=Output
                if algo.generation >= GenerationMax:
                    break
        datachart[Nameinput]["IsEnabel"] = False

button.on_click(lambda : callback(button))

genetic_tab_column = column(row0,row1,row2,row3,row4,row5_2,row5)

genetic_algo_tab = TabPanel(title="Genetic Algorithm", child=genetic_tab_column)
pso_algo_tab = TabPanel(title="PSO Algorithm", child=figure())
ant_colony_tab = TabPanel(title="Ant Colony", child=figure())

algorithm_tabs = Tabs(tabs=[genetic_algo_tab, pso_algo_tab, ant_colony_tab])

root_page.add_root(column(file_input,row(graph_box, algorithm_tabs)))

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