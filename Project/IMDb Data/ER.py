from graphviz import Graph


def add_entity(dot, name, label, x, y, width=1.8, height=0.45):
    dot.node(
        name,
        label,
        shape="box",
        style="filled",
        fillcolor="#eaf1ff",
        color="black",
        fontcolor="#0b2c73",
        fontsize="14",
        width=str(width),
        height=str(height),
        pos=f"{x},{y}!",
    )


def add_attribute(dot, entity, attr, x, y):
    node_name = f"{entity}_{attr}"

    if attr == "id":
        label = "<<U>id</U>>"
    else:
        label = attr

    dot.node(
        node_name,
        label,
        shape="ellipse",
        style="filled",
        fillcolor="white",
        color="black",
        fontsize="10",
        width="1.1",
        height="0.35",
        pos=f"{x},{y}!",
    )

    dot.edge(node_name, entity)


def add_relationship(dot, name, label, x, y):
    dot.node(
        name,
        label,
        shape="diamond",
        style="filled",
        fillcolor="#fff3d6",
        color="black",
        fontcolor="#8a5a00",
        fontsize="10",
        width="1.2",
        height="0.55",
        pos=f"{x},{y}!",
    )


def add_arrow(dot, start, end, label=""):
    dot.edge(
        start,
        end,
        label=label,
        fontsize="10",
        color="black",
        arrowsize="0.7",
    )


def build_diagram():
    dot = Graph(
        "WhatShouldIWatchTonight_ER",
        engine="neato",
        format="png"
    )

    dot.attr(
        bgcolor="white",
        overlap="false",
        splines="true",
        outputorder="edgesfirst",
        label="ER Diagram — WhatShouldIWatchTonight",
        labelloc="t",
        fontsize="22",
        fontcolor="#0b2c73",
    )

    dot.attr("node", fontname="Arial")
    dot.attr("edge", fontname="Arial", color="black")

    # -------------------------
    # Entities
    # -------------------------

    add_entity(dot, "Movie", "Movie", 5, 9)
    add_entity(dot, "Actor", "Actor", 1.2, 8.7)
    add_entity(dot, "Genre", "Genre", 8.8, 8.7)
    add_entity(dot, "Mood", "Mood", 5, 6.6)

    add_entity(dot, "QuizAnswerOption", "QuizAnswerOption", 2.8, 4.5, width=2.2)
    add_entity(dot, "QuizQuestion", "QuizQuestion", 7.2, 4.5, width=2.0)

    add_entity(dot, "QuizAttempt", "QuizAttempt", 1.8, 1.5, width=1.8)
    add_entity(dot, "QuizResponse", "QuizResponse", 5.5, 1.5, width=2.0)

    # -------------------------
    # Attributes
    # -------------------------

    add_attribute(dot, "Movie", "id", 3.8, 10.0)
    add_attribute(dot, "Movie", "title", 4.6, 10.2)
    add_attribute(dot, "Movie", "release_year", 5.6, 10.2)
    add_attribute(dot, "Movie", "rating", 6.6, 10.0)
    add_attribute(dot, "Movie", "poster_url", 4.4, 8.2)
    add_attribute(dot, "Movie", "duration_min", 5.8, 8.2)

    add_attribute(dot, "Actor", "id", 0.7, 9.7)
    add_attribute(dot, "Actor", "name", 1.7, 9.7)

    add_attribute(dot, "Genre", "id", 8.3, 9.7)
    add_attribute(dot, "Genre", "name", 9.3, 9.7)

    add_attribute(dot, "Mood", "id", 4.5, 5.8)
    add_attribute(dot, "Mood", "name", 5.5, 5.8)

    add_attribute(dot, "QuizAnswerOption", "id", 1.3, 5.3)
    add_attribute(dot, "QuizAnswerOption", "option_text", 1.0, 4.5)
    add_attribute(dot, "QuizAnswerOption", "sort_order", 1.3, 3.7)

    add_attribute(dot, "QuizQuestion", "id", 8.8, 5.3)
    add_attribute(dot, "QuizQuestion", "question_text", 9.2, 4.5)
    add_attribute(dot, "QuizQuestion", "sort_order", 8.8, 3.7)

    add_attribute(dot, "QuizAttempt", "id", 0.7, 2.4)
    add_attribute(dot, "QuizAttempt", "session_id", 0.6, 1.5)
    add_attribute(dot, "QuizAttempt", "created_at", 0.7, 0.6)

    add_attribute(dot, "QuizResponse", "id", 4.2, 0.5)
    add_attribute(dot, "QuizResponse", "attempt_id", 5.0, 0.35)
    add_attribute(dot, "QuizResponse", "question_id", 6.0, 0.35)
    add_attribute(dot, "QuizResponse", "answer_opt_id", 7.0, 0.5)

    # -------------------------
    # Relationships
    # -------------------------

    add_relationship(dot, "features", "features", 3.0, 8.8)
    add_relationship(dot, "categorised_in", "categorised in", 7.0, 8.8)
    add_relationship(dot, "matches", "matches", 5.0, 7.7)

    add_relationship(dot, "points_to", "points to", 3.5, 5.8)
    add_relationship(dot, "suggests", "suggests", 7.1, 5.8)

    add_relationship(dot, "has", "has", 5.0, 4.5)
    add_relationship(dot, "selected_in", "selected in", 3.1, 3.0)
    add_relationship(dot, "answered_in", "answered in", 7.0, 3.0)
    add_relationship(dot, "contains", "contains", 3.6, 1.5)

    # -------------------------
    # Entity relationships with arrows
    # -------------------------

    add_arrow(dot, "Movie", "features", "M")
    add_arrow(dot, "features", "Actor", "M")

    add_arrow(dot, "Movie", "categorised_in", "M")
    add_arrow(dot, "categorised_in", "Genre", "M")

    add_arrow(dot, "Movie", "matches", "M")
    add_arrow(dot, "matches", "Mood", "M")

    add_arrow(dot, "QuizAnswerOption", "points_to", "M")
    add_arrow(dot, "points_to", "Mood", "M")

    add_arrow(dot, "QuizAnswerOption", "suggests", "M")
    add_arrow(dot, "suggests", "Genre", "M")

    add_arrow(dot, "QuizQuestion", "has", "1")
    add_arrow(dot, "has", "QuizAnswerOption", "N")

    add_arrow(dot, "QuizAnswerOption", "selected_in", "1")
    add_arrow(dot, "selected_in", "QuizResponse", "N")

    add_arrow(dot, "QuizQuestion", "answered_in", "1")
    add_arrow(dot, "answered_in", "QuizResponse", "N")

    add_arrow(dot, "QuizAttempt", "contains", "1")
    add_arrow(dot, "contains", "QuizResponse", "N")

    return dot


if __name__ == "__main__":
    diagram = build_diagram()
    diagram.render("whatshouldiwatchtonight_er_fixed", cleanup=True)
    print("Diagram saved as whatshouldiwatchtonight_er_fixed.png")