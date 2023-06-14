import pandas as pd
import networkx as nx
from bokeh.io import curdoc
from bokeh.layouts import column, row
from bokeh.models import ColumnDataSource,ColorPicker,HoverTool,PreText,FileInput, Tabs,TabPanel,Label,Slider,NumericInput, Button, Select,RadioButtonGroup,AutocompleteInput
from bokeh.plotting import figure,from_networkx
from bokeh.palettes import Category20_20
import random
from pso import PSO 
from genetic import  Genetic
from antcolony import AntColony
G = None
datachart_genetic = {}
datachart_pso = {}
datachart_aco = {}
#Algorithms
def fitness_function(path):
    global G
    fitness = 0
    for i,v in enumerate(path):
        try:
            if i == len(path)-1:
                fitness+= G.adj[v][path[0]]['w']
            else:
                fitness+= G.adj[v][path[i+1]]['w']
        except:
            try:
                fitness += 1000000
            except:
                pass
    try:
        fitness+= G.adj[path[-1]][path[0]]['w']
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
    global datachart_genetic,Name_auto_complete_input,Generation_numericalinput
    Nameinput = Name_auto_complete_input.value_input
    GenerationMax = Generation_numericalinput.value
    if Nameinput in datachart_genetic.keys():
        if datachart_genetic[Nameinput]["IsEnabel"]:
            print("already running!")
        else:
            lineChart = None

            for i in genetic_figure.renderers:
                if i.name == Nameinput:
                    lineChart = i
            datachart_genetic[Nameinput]["IsEnabel"] = True
            algo = datachart_genetic[Nameinput]["algorithm"]
            
            if algo.generation < GenerationMax:
                for i in algo.Execute():
                    print(f"Generation : {algo.generation}\tFitness : {algo.best.fitness}")
                    datachart_genetic[Nameinput]["generation"].append(algo.generation)
                    datachart_genetic[Nameinput]["fitness"].append(algo.best.fitness)

                    lineChart.data_source.stream({"Generation":[algo.generation] , "Fitness":[algo.best.fitness]})
                    Output = PreText(text=f"Generation: {algo.generation}\nBest : \n\tGeneration: {algo.bestgen}\tFitness: {algo.best.fitness}\n\tGene: {algo.best.gene+[algo.best.gene[0]]}", width=200, height=75)
                    row5_2.children[0]=Output
                    if algo.generation >= GenerationMax:
                        break
            datachart_genetic[Nameinput]["IsEnabel"] = False

    else:
        algo = Genetic(fitness_function,population_numeric_input.value,mutation_rate_slider.value
                            ,random_gene_maker,{'type':crossover_type_select.value},{'type':mutation_type_select.value},
                            True,selection_label[selection_type_select.active],
                            replacement_label[replacement_type_select.active],[selection_numeric_input.value,(population_numeric_input.value//selection_numeric_input.value)])
        datachart_genetic.update({Nameinput:{"algorithm":algo,"IsEnabel":True,"generation":[],"fitness":[]}})
        

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
                datachart_genetic[Nameinput]["generation"].append(algo.generation)
                datachart_genetic[Nameinput]["fitness"].append(algo.best.fitness)
                line.data_source.stream({"Generation":[algo.generation] , "Fitness":[algo.best.fitness]})
                Output = PreText(text=f"Generation: {algo.generation}\nBest : \n\tGeneration: {algo.bestgen}\tFitness: {algo.best.fitness}\n\tGene: {algo.best.gene+[algo.best.gene[0]]}", width=200, height=75)
                row5_2.children[0]=Output
                if algo.generation >= GenerationMax:
                    break
        datachart_genetic[Nameinput]["IsEnabel"] = False

button.on_click(lambda : callback(button))

genetic_tab_column = column(row0,row1,row2,row3,row4,row5_2,row5)

# PSO
Name_auto_complete_input_pso = AutocompleteInput(title="Name:", completions=[])
row0_pso = row(Name_auto_complete_input_pso)
Itrations_numericalinput = NumericInput(value=50,low=1,high=1000,title="Number of Itrations:")
NumParticle_numericalinput = NumericInput(value=50,low=1,high=1000,title="Number of Particles:")
row0_2_pso = row(Itrations_numericalinput,NumParticle_numericalinput)

inertia_slider = Slider(start=0, end=1, value=0.5, step=0.01, title="Inertia weight")
row1_pso = row(inertia_slider)
c1_slider = Slider(start=0, end=10, value=1, step=0.01, title="Personal coeficent")
c2_slider = Slider(start=0, end=10, value=1, step=0.01, title="Global coeficent")
row1_2_pso = row(c1_slider,c2_slider)

button_pso = Button(label='start', button_type="primary")
colorpicker_pso = ColorPicker(title="Line Color")
row2_pso = row(button_pso,colorpicker_pso)

Output_pso = PreText(text="", width=0, height=0)
row3_pso=row(Output_pso)

pso_figure=figure(title="PSO Algorithm", x_axis_label="Itration", y_axis_label="Gbest Fitness")
pso_figure.add_tools(HoverTool(tooltips="Itration: @Itration, Fitness: @Fitness", mode="vline"))
row4_pso=row(pso_figure)

def callback(b:Button):
    print("on start pso")
    global datachart_pso,Name_auto_complete_input_pso,Itrations_numericalinput
    Nameinput = Name_auto_complete_input_pso.value_input
    ItrationMax = Itrations_numericalinput.value
    if Nameinput in datachart_pso.keys():
        if datachart_pso[Nameinput]["IsEnabel"]:
            print("already running!")
        else:
            lineChart = None

            for i in pso_figure.renderers:
                if i.name == Nameinput:
                    lineChart = i
            datachart_pso[Nameinput]["IsEnabel"] = True
            algo = datachart_pso[Nameinput]["algorithm"]
            
            if algo.itration_num < ItrationMax:
                for i in algo.Execute():
                    print(f"Itration : {algo.itration_num}\tGBest Fitness : {algo.gbest.fitness}")
                    datachart_pso[Nameinput]["itration"].append(algo.itration_num)
                    datachart_pso[Nameinput]["fitness"].append(algo.gbest.fitness)

                    lineChart.data_source.stream({"Itration":[algo.itration_num] , "Fitness":[algo.gbest.fitness]})
                    Output_pso = PreText(text=f"Itration: {algo.itration_num}\nGlobal Best : \n\tItration: {algo.gbest_itration}\tFitness: {algo.gbest.fitness}\n\tS: {algo.gbest.S+[algo.best.S[0]]}", width=200, height=75)
                    row3_pso.children[0]=Output_pso
                    if algo.itration_num >= ItrationMax:
                        break
            datachart_pso[Nameinput]["IsEnabel"] = False

    else:
        algo = PSO(NumParticle_numericalinput.value,
                G,fitness_function,inertia_slider.value
                ,c1_slider.value,c2_slider.value)
        datachart_pso.update({Nameinput:{"algorithm":algo,"IsEnabel":True,"itration":[],"fitness":[]}})
        

        data = {'Itration': [],
                'Fitness': []}
        source = ColumnDataSource(data=data)

        line = pso_figure.line(legend_label=Nameinput,
                            name=Nameinput,
                            color=colorpicker_pso.color,
                            line_width=2,x="Itration",y="Fitness",source=source)
        pso_figure.legend.click_policy="mute"
        Name_auto_complete_input_pso.completions.append(Nameinput)

        if algo.itration_num < ItrationMax:
            for i in algo.Execute():
                print(f"Itration : {algo.itration_num}\tFitness : {algo.gbest.fitness}")
                datachart_pso[Nameinput]["itration"].append(algo.itration_num)
                datachart_pso[Nameinput]["fitness"].append(algo.gbest.fitness)
                line.data_source.stream({"Itration":[algo.itration_num] , "Fitness":[algo.gbest.fitness]})
                Output_pso = PreText(text=f"Itration: {algo.itration_num}\nGlobal Best : \n\tItration: {algo.gbest_itration}\tFitness: {algo.gbest.fitness}\n\tS: {algo.gbest.S+[algo.best.S[0]]}", width=200, height=75)
                row3_pso.children[0]=Output_pso
                if algo.itration_num >= ItrationMax:
                    break
        datachart_pso[Nameinput]["IsEnabel"] = False

button_pso.on_click(lambda : callback(button_pso))

Pso_tab_column = column(row0_pso,row0_2_pso,row1_pso,row1_2_pso,row2_pso,row3_pso,row4_pso)


# ACO
Name_auto_complete_input_aco = AutocompleteInput(title="Name:", completions=[])
row0_aco = row(Name_auto_complete_input_aco)
Itrations_aco_numericalinput = NumericInput(value=50,low=1,high=1000,title="Number of Itrations:")
NumAnt_numericalinput = NumericInput(value=50,low=1,high=1000,title="Number of Ant:")
row0_2_aco = row(Itrations_aco_numericalinput,NumAnt_numericalinput)

evaporation_slider = Slider(start=0, end=1, value=0.5, step=0.01, title="Evaporation rate")
init_pheromone_slider = Slider(start=0, end=1, value=0.5, step=0.1, title="Initial pheromone")
row1_aco = row(evaporation_slider,init_pheromone_slider)
alpha_slider = Slider(start=0, end=10, value=1, step=0.01, title="Alpha")
beta_slider = Slider(start=0, end=10, value=1, step=0.01, title="Beta")
row1_2_aco = row(alpha_slider,beta_slider)

button_aco = Button(label='start', button_type="primary")
colorpicker_aco = ColorPicker(title="Line Color")
row2_aco = row(button_aco,colorpicker_aco)

Output_aco = PreText(text="", width=0, height=0)
row3_aco=row(Output_aco)

aco_figure=figure(title="ACO Algorithm", x_axis_label="Itration", y_axis_label="Best")
aco_figure.add_tools(HoverTool(tooltips="Itration: @Itration, Distance: @Distance", mode="vline"))
row4_aco=row(aco_figure)

def callback(b:Button):
    print("on start aco")
    global datachart_aco,Name_auto_complete_input_aco,Itrations_aco_numericalinput
    Nameinput = Name_auto_complete_input_aco.value_input
    ItrationMax = Itrations_aco_numericalinput.value
    if Nameinput in datachart_aco.keys():
        if datachart_aco[Nameinput]["IsEnabel"]:
            print("already running!")
        else:
            lineChart = None

            for i in aco_figure.renderers:
                if i.name == Nameinput:
                    lineChart = i
            datachart_aco[Nameinput]["IsEnabel"] = True
            algo = datachart_aco[Nameinput]["algorithm"]
            
            if algo.itration_num < ItrationMax:
                for i in algo.Execute():
                    best=min(algo.ants,key=lambda x:x.distance)
                    print(f"Itration : {algo.itration_num}\tGBest Distance : {best.distance}")
                    datachart_aco[Nameinput]["itration"].append(algo.itration_num)
                    datachart_aco[Nameinput]["distance"].append(best.distance)

                    lineChart.data_source.stream({"Itration":[algo.itration_num] , "Distance":[best.distance]})
                    Output_aco = PreText(text=f"Itration: {algo.itration_num}\nBest : \n\tDistance: {best.distance}\n\tPath: {best.path}", width=200, height=75)
                    row3_aco.children[0]=Output_aco
                    if algo.itration_num >= ItrationMax:
                        break
            datachart_aco[Nameinput]["IsEnabel"] = False

    else:
        algo = AntColony(NumAnt_numericalinput.value,alpha_slider.value,
                        beta_slider.value,evaporation_slider.value,
                        init_pheromone_slider.value,G)
        datachart_aco.update({Nameinput:{"algorithm":algo,"IsEnabel":True,"itration":[],"distance":[]}})
        

        data = {'Itration': [],
                'Distance': []}
        source = ColumnDataSource(data=data)

        line = aco_figure.line(legend_label=Nameinput,
                            name=Nameinput,
                            color=colorpicker_aco.color,
                            line_width=2,x="Itration",y="Distance",source=source)
        aco_figure.legend.click_policy="mute"
        Name_auto_complete_input_aco.completions.append(Nameinput)

        if algo.itration_num < ItrationMax:
            for i in algo.Execute():
                best=min(algo.ants,key=lambda x:x.distance)
                print(f"Itration : {algo.itration_num}\tGBest Distance : {best.distance}")
                datachart_aco[Nameinput]["itration"].append(algo.itration_num)
                datachart_aco[Nameinput]["distance"].append(best.distance)

                lineChart.data_source.stream({"Itration":[algo.itration_num] , "Distance":[best.distance]})
                Output_aco = PreText(text=f"Itration: {algo.itration_num}\nBest : \n\tDistance: {best.distance}\n\tPath: {best.path}", width=200, height=75)
                row3_aco.children[0]=Output_aco
                if algo.itration_num >= ItrationMax:
                    break
        datachart_aco[Nameinput]["IsEnabel"] = False

button_aco.on_click(lambda : callback(button_aco))

aco_tab_column = column(row0_aco,row0_2_aco,row1_aco,row1_2_aco,row2_aco,row3_aco,row4_aco)


genetic_algo_tab = TabPanel(title="Genetic Algorithm", child=genetic_tab_column)
pso_algo_tab = TabPanel(title="PSO Algorithm", child=Pso_tab_column)
ant_colony_tab = TabPanel(title="Ant Colony", child=aco_tab_column)

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