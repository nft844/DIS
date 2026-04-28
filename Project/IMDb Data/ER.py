from graphviz import Digraph


def add_entity(dot, name, attributes):
    """
    Creates an ER entity as a rectangle and its attributes as ovals.
    attributes should be a list of strings.
    Use "id" for primary keys; it will be underlined visually.
    """
    dot.node(name, name, shape="box", style="filled", fillcolor="#eaf1ff",
             color="black", fontcolor="#0b2c73", fontsize="16", penwidth="1.6")

    for attr in attributes:
        attr_node = f"{name}_{attr}"

        # Underline id attributes using HTML-like labels
        if attr == "id":
            label = "<<U>id</U>>"
        else:
            label = attr

        dot.node(attr_node, label, shape="ellipse", style="filled",
                 fillcolor="white", color="black", fontsize="11")

        dot.edge(attr_node, name, arrowhead="none")


def add_relationship(dot, left, rel_name, right, left_card, right_card):
    """
    Creates a relationship diamond between two entities.
    Preserves arrows.
    Example:
    Movie -- features -- Actor, M:M
    """
    rel_node = f"{left}_{rel_name}_{right}".replace(" ", "_")

    dot.node(rel_node, rel_name, shape="diamond", style="filled",
             fillcolor="#fff3d6", color="black", fontcolor="#8a5a00",
             fontsize="11", penwidth="1.4")

    # Left entity -> relationship
    dot.edge(left, rel_node, label=left_card, fontsize="11", arrowhead="normal")

    # Relationship -> right entity
    dot.edge(rel_node, right, label=right_card, fontsize="11", arrowhead="normal")


def build_er_diagram():
    dot = Digraph("WhatShouldIWatchTonight_ER", format="png")

    dot.attr(
        rankdir="TB",
        bgcolor="white",
        splines="ortho",
        nodesep="0.7",
        ranksep="1.0",
        label="ER Diagram — WhatShouldIWatchTonight",
        labelloc="t",
        fontsize="22",
        fontcolor="#0b2c73"
    )

    dot.attr("node", fontname="Arial")
    dot.attr("edge", fontname="Arial", color="black", arrowsize="0.8")

    # -------------------------
    # Entities
    # -------------------------

    add_entity(dot, "Movie", [
        "id",
        "title",
        "release_year",
        "rating",
        "poster_url",
        "duration_min"
    ])

    add_entity(dot, "Actor", [
        "id",
        "name"
    ])

    add_entity(dot, "Genre", [
        "id",
        "name"
    ])

    add_entity(dot, "Mood", [
        "id",
        "name"
    ])

    add_entity(dot, "QuizQuestion", [
        "id",
        "question_text",
        "sort_order"
    ])

    add_entity(dot, "QuizAnswerOption", [
        "id",
        "option_text",
        "sort_order"
    ])

    add_entity(dot, "QuizAttempt", [
        "id",
        "session_id",
        "created_at"
    ])

    add_entity(dot, "QuizResponse", [
        "id",
        "attempt_id",
        "question_id",
        "answer_opt_id"
    ])

    # -------------------------
    # Layout helpers
    # -------------------------

    # Keep some entities on roughly the same horizontal levels
    with dot.subgraph() as s:
        s.attr(rank="same")
        s.node("Actor")
        s.node("Movie")
        s.node("Genre")

    with dot.subgraph() as s:
        s.attr(rank="same")
        s.node("QuizAnswerOption")
        s.node("QuizQuestion")

    with dot.subgraph() as s:
        s.attr(rank="same")
        s.node("QuizAttempt")
        s.node("QuizResponse")

    # -------------------------
    # Relationships
    # -------------------------

    add_relationship(dot, "Movie", "features", "Actor", "M", "M")

    add_relationship(dot, "Movie", "categorised in", "Genre", "M", "M")

    add_relationship(dot, "Movie", "matches", "Mood", "M", "M")

    add_relationship(dot, "QuizQuestion", "has", "QuizAnswerOption", "1", "N")

    add_relationship(dot, "QuizAnswerOption", "points to", "Mood", "M", "M")

    add_relationship(dot, "QuizAnswerOption", "suggests", "Genre", "M", "M")

    add_relationship(dot, "QuizAttempt", "contains", "QuizResponse", "1", "N")

    add_relationship(dot, "QuizQuestion", "answered in", "QuizResponse", "1", "N")

    add_relationship(dot, "QuizAnswerOption", "selected in", "QuizResponse", "1", "N")

    return dot


if __name__ == "__main__":
    diagram = build_er_diagram()

    # Creates whatshouldiwatchtonight_er.png
    diagram.render("whatshouldiwatchtonight_er", cleanup=True)

    print("Diagram saved as whatshouldiwatchtonight_er.png")
    