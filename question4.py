import streamlit as st
import networkx as nx
import matplotlib.pyplot as plt

# Define the satisfaction matrix and other necessary data
profs = ['P1', 'P2', 'P3']
courses = ['Marketing', 'Finance', 'Production']
semesters = ['Fall', 'Spring']

# Function to create the graph and solve min-cost flow
def create_min_cost_flow(satisfaction):
    G = nx.DiGraph()

    # Source and sink
    G.add_node("S", demand=-12)
    G.add_node("T", demand=12)

    # Add nodes and edges
    for p in profs:
        for sem in semesters:
            node_ps = f"{p}_{sem}"
            G.add_node(node_ps)
            G.add_edge("S", node_ps, capacity=2, weight=0)  # 2 courses per semester per prof

            for c in courses:
                node_cs = f"{c}_{sem}"
                G.add_node(node_cs)
                cost = -satisfaction[p][sem][c]  # Negative satisfaction for min-cost
                G.add_edge(node_ps, node_cs, capacity=1, weight=cost)

    # Course-semester → Course and Course → Sink
    for c in courses:
        for sem in semesters:
            node_cs = f"{c}_{sem}"
            G.add_edge(node_cs, c, capacity=4, weight=0)  # up to 4 total per course
        G.add_edge(c, "T", capacity=4, weight=0)

    # Solve min-cost flow
    flowDict = nx.min_cost_flow(G)

    return flowDict, satisfaction


# Streamlit interface
st.title("University Course Assignment Optimizer")

# Requirements Text
st.write("""
### Problem Overview:
A university has three professors (P1, P2, and P3) who each teach four courses per year. 
The courses offered are:
- Marketing
- Finance
- Production

Each year, four sections of each course (Marketing, Finance, Production) must be taught—two in the Fall semester and two in the Spring semester. 
At least one section of each course must be taught in each semester.

### Objective:
The goal is to assign professors to courses and semesters so as to **maximize the total satisfaction** of the professors. 

Each professor has:
- A **semester preference** (how much they like to teach in either Fall or Spring)
- A **course preference** (how much they enjoy teaching a specific course).

The total satisfaction for a professor teaching a course is the sum of the semester preference and the course preference. For example, Professor 1 derives a satisfaction of 3 (Fall preference) + 6 (Marketing preference) = **9** for teaching Marketing in the Fall.

### Constraints:
- Each professor must teach **exactly 2 courses per semester**.
- Each course must be assigned to **exactly 4 sections** in total over both semesters.

---

### How This Works:
- You can adjust the preferences for each professor and each course.
- Click **Solve** to compute the optimal assignments of professors to courses using a **minimum cost network flow** optimization approach.
- The optimal assignments maximize the total satisfaction for all professors.

""")

# Input form for preferences
st.sidebar.header("Professor Preferences")
satisfaction = {p: {sem: {c: st.slider(f"{p} {sem} {c}", min_value=1, max_value=10, value=5) 
                          for c in courses} 
                   for sem in semesters} 
               for p in profs}

# Solve the problem
if st.button("Solve"):
    flowDict, satisfaction = create_min_cost_flow(satisfaction)

    # Extract assignments
    assignments = []
    total_satisfaction = 0

    for p in profs:
        for sem in semesters:
            node_ps = f"{p}_{sem}"
            for c in courses:
                node_cs = f"{c}_{sem}"
                if flowDict[node_ps].get(node_cs, 0) == 1:
                    sat = satisfaction[p][sem][c]
                    total_satisfaction += sat
                    assignments.append((p, sem, c, sat))

    # Display the assignments
    st.write("### Assignments:")
    for a in assignments:
        st.write(f"Professor {a[0]} teaches {a[2]} in {a[1]} (Satisfaction: {a[3]})")

    st.write(f"### Total Satisfaction: {total_satisfaction}")

    # Network visualization
    G = nx.DiGraph()
    # Rebuild the graph to plot the flow network (as done in the previous code)
    for p in profs:
        for sem in semesters:
            node_ps = f"{p}_{sem}"
            G.add_node(node_ps)
            G.add_edge("S", node_ps, capacity=2, weight=0)

            for c in courses:
                node_cs = f"{c}_{sem}"
                G.add_node(node_cs)
                cost = -satisfaction[p][sem][c]
                G.add_edge(node_ps, node_cs, capacity=1, weight=cost)

    for c in courses:
        for sem in semesters:
            node_cs = f"{c}_{sem}"
            G.add_edge(node_cs, c, capacity=4, weight=0)
        G.add_edge(c, "T", capacity=4, weight=0)

    pos = nx.spring_layout(G, seed=42)
    plt.figure(figsize=(10, 8))
    nx.draw_networkx_nodes(G, pos, node_size=500, node_color='skyblue')
    nx.draw_networkx_edges(G, pos, width=2, alpha=0.5, edge_color='black')
    nx.draw_networkx_labels(G, pos, font_size=12, font_weight='bold')

    # Display plot
    st.pyplot(plt)
