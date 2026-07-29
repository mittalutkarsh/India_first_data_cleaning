"""Emit editable draw.io companions for the two architecture figures in
v5_playbook.html, following the ml-pipeline-diagram-utkarsh skill (economist
style: tinted regions, cylinder3 data sources, rounded process boxes,
orthogonal labelled arrows). Open in https://app.diagrams.net to restyle."""

# palette matched to the page figures
LANE = {
    "code":        ("#2E357E", "#ECEEF8"),
    "agentic":     ("#B5476B", "#FBEEF3"),
    "reasoning":   ("#E0982B", "#FBF1E0"),
    "general web": ("#656579", "#F1F2F8"),
    "indic":       ("#147D74", "#E6F3F0"),
}

COMPOSE = [
    ("code", "SWE-bench Verified", "Stack v2 + repo-fix traces"),
    ("agentic", "Terminal-Bench / &#964;-bench / GAIA", "generated tool-use trajectories"),
    ("reasoning", "AIME / FrontierMath", "distilled step-by-step traces"),
    ("general web", "MMLU / MMLU-Pro", "DCLM / FineWeb"),
    ("indic", "MILU / IndicGenBench", "Sangraha / IndicCorp / Wiki"),
]

PHASES = [("Foundation", 45, "#2E357E", "#ECEEF8"),
          ("Expansion", 30, "#147D74", "#E6F3F0"),
          ("Reasoning + LC", 23, "#E0982B", "#FBF1E0"),
          ("Anneal", 2, "#B5476B", "#FBEEF3")]

SKEL = ('<mxfile host="app.diagrams.net" agent="Claude" version="24.0.0">\n'
        '  <diagram name="{name}" id="{slug}">\n'
        '    <mxGraphModel dx="2000" dy="1400" grid="1" gridSize="10" guides="1" tooltips="1" '
        'connect="1" arrows="1" fold="1" page="1" pageScale="1" pageWidth="1600" pageHeight="1200" '
        'math="0" shadow="0">\n      <root>\n        <mxCell id="0" />\n'
        '        <mxCell id="1" parent="0" />\n{cells}      </root>\n'
        '    </mxGraphModel>\n  </diagram>\n</mxfile>\n')


def cell(i, value, style, x, y, w, h):
    return ('        <mxCell id="c%d" value="%s" style="%s" vertex="1" parent="1">\n'
            '          <mxGeometry x="%d" y="%d" width="%d" height="%d" as="geometry" />\n'
            '        </mxCell>\n' % (i, value, style, x, y, w, h))


def edge(i, src, dst):
    st = ('edgeStyle=orthogonalEdgeStyle;rounded=0;html=1;endArrow=classic;endFill=1;'
          'strokeColor=#5A5A6E;strokeWidth=1.5;')
    return ('        <mxCell id="e%d" style="%s" edge="1" parent="1" source="c%d" target="c%d">\n'
            '          <mxGeometry relative="1" as="geometry" />\n        </mxCell>\n'
            % (i, st, src, dst))


def compose_drawio():
    cells, i = "", 2
    cells += cell(i, "COMPOSE BACKWARD: benchmark fixes the lane, dataset satisfies the benchmark",
                  "text;html=1;strokeColor=none;fillColor=none;align=left;fontSize=13;fontStyle=1;fontColor=#1F1F3A;",
                  40, 30, 900, 24); i += 1
    y = 80
    for lane, bench, ds in COMPOSE:
        acc, fill = LANE[lane]
        lane_id = i
        cells += cell(i, lane, "rounded=1;whiteSpace=wrap;html=1;fillColor=%s;strokeColor=%s;fontColor=%s;"
                      "fontStyle=1;fontSize=13;arcSize=10;" % (fill, acc, acc), 40, y, 200, 50); i += 1
        bench_id = i
        cells += cell(i, bench, "rounded=1;whiteSpace=wrap;html=1;fillColor=#FFFFFF;strokeColor=#6169B8;"
                      "fontSize=12;arcSize=10;", 340, y, 360, 50); i += 1
        ds_id = i
        cells += cell(i, ds, "shape=cylinder3;whiteSpace=wrap;html=1;boundedLbl=1;backgroundOutline=1;size=12;"
                      "fillColor=#FFFFFF;strokeColor=%s;strokeWidth=1.5;fontSize=11;" % acc, 800, y - 8, 240, 66); i += 1
        cells += edge(i, lane_id, bench_id); i += 1
        cells += edge(i, ds_id, bench_id); i += 1
        y += 90
    return SKEL.format(name="V5 Compose Backward", slug="compose-backward", cells=cells)


def curriculum_drawio():
    cells, i = "", 2
    cells += cell(i, "CURRICULUM PHASES across the 3T-token budget (training order, left to right)",
                  "text;html=1;strokeColor=none;fillColor=none;align=left;fontSize=13;fontStyle=1;fontColor=#1F1F3A;",
                  40, 30, 1000, 24); i += 1
    x, total_w = 40, 1200
    for name, pct, acc, fill in PHASES:
        w = round(total_w * pct / 100)
        cells += cell(i, "&lt;b&gt;%s&lt;/b&gt;&lt;br&gt;&lt;span style='font-size:16px'&gt;%d%%&lt;/span&gt;" % (name, pct),
                      "rounded=1;whiteSpace=wrap;html=1;fillColor=%s;strokeColor=%s;fontColor=%s;"
                      "arcSize=8;verticalAlign=middle;fontSize=12;" % (fill, acc, acc), x, 90, w, 120); i += 1
        x += w
    cells += cell(i, "max sequence length rises left &#8594; right; transitions gradual (overlapping bands)",
                  "text;html=1;strokeColor=none;fillColor=none;align=left;fontSize=11;fontColor=#656579;fontStyle=2;",
                  40, 224, 1000, 20); i += 1
    return SKEL.format(name="V5 Curriculum Phases", slug="curriculum-phases", cells=cells)


if __name__ == "__main__":
    with open("compose_backward.drawio", "w", encoding="utf-8") as f:
        f.write(compose_drawio())
    with open("curriculum_phases.drawio", "w", encoding="utf-8") as f:
        f.write(curriculum_drawio())
    print("Done. compose_backward.drawio, curriculum_phases.drawio written.")
