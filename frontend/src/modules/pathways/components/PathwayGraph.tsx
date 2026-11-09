
import { useEffect, useRef } from "react";
import cytoscape, {
  type Core,
  type ElementDefinition,
  type NodeSingular,
} from "cytoscape";

import type {
  PathwaySceneResponse,
} from "../../../core/types";

import "./PathwayGraph.css";

interface PathwayGraphProps {
  scene: PathwaySceneResponse;
  selectedNodeIdentity: string | null;
  onNodeSelect: (identity: string | null) => void;
}

function createGraphElements(
  scene: PathwaySceneResponse,
): ElementDefinition[] {
  const nodes: ElementDefinition[] = scene.nodes.map((node) => ({
    group: "nodes",
    data: {
      id: node.identity,
      label: node.label,
      nodeType: node.node_type,
    },
    position: {
      x: node.x,
      y: node.y,
    },
  }));

  const edges: ElementDefinition[] = scene.edges.map(
    (edge, index) => ({
      group: "edges",
      data: {
        id: `edge-${index}`,
        source: edge.source_identity,
        target: edge.target_identity,
        role: edge.role,
        label:
          edge.coefficient === "1"
            ? ""
            : edge.coefficient,
      },
    }),
  );

  return [...nodes, ...edges];
}

export function PathwayGraph({
  scene,
  selectedNodeIdentity,
  onNodeSelect,
}: PathwayGraphProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const graphRef = useRef<Core | null>(null);

  const lastTapRef = useRef<{
    nodeId: string;
    time: number;
  } | null>(null);

  function focusNode(
    graph: Core,
    node: NodeSingular,
  ): void {
    if (node.empty()) {
      return;
    }

    graph.animate(
      {
        center: {
          eles: node,
        },
        zoom: Math.max(graph.zoom(), 1.5),
      },
      {
        duration: 400,
        easing: "ease-in-out-cubic",
      },
    );
  }

  useEffect(() => {
    const container = containerRef.current;

    if (!container) {
      return;
    }

    const graph = cytoscape({
      container,
      elements: createGraphElements(scene),

      layout: {
        name: "preset",
        fit: true,
        padding: 70,
      },

      minZoom: 0.1,
      maxZoom: 4,
      wheelSensitivity: 0.2,

      style: [
        {
          selector: "node",
          style: {
            label: "data(label)",
            color: "#e8edf7",
            "font-size": 12,
            "font-weight": 500,
            "text-wrap": "wrap",
            "text-max-width": "110px",
            "text-valign": "center",
            "text-halign": "center",
            "border-width": 1.5,
            "border-opacity": 1,
            width: 100,
            height: 52,
            "overlay-opacity": 0,
          },
        },
        {
          selector: 'node[nodeType = "metabolite"]',
          style: {
            shape: "ellipse",
            "background-color": "#173d38",
            "border-color": "#438e78",
            color: "#b7f0d9",
            width: 110,
            height: 58,
          },
        },
        {
          selector: 'node[nodeType = "reaction"]',
          style: {
            shape: "round-rectangle",
            "background-color": "#303b50",
            "border-color": "#7289b4",
            color: "#d7e2ff",
            width: 120,
            height: 54,
          },
        },
        {
          selector: "node:selected",
          style: {
            "border-color": "#72b99c",
            "border-width": 3,
            "overlay-color": "#72b99c",
            "overlay-opacity": 0.12,
          },
        },
        {
          selector: "edge",
          style: {
            width: 2,
            "line-color": "#64758b",
            "target-arrow-color": "#72b99c",
            "target-arrow-shape": "triangle",
            "arrow-scale": 1.1,
            "curve-style": "bezier",
            label: "data(label)",
            color: "#aebbd0",
            "font-size": 10,
            "font-weight": 500,
            "text-background-color": "#101720",
            "text-background-opacity": 0.9,
            "text-background-padding": "3px",
            "text-rotation": "autorotate",
            "text-margin-y": -9,
            "overlay-opacity": 0,
          },
        },
        {
          selector: 'edge[role = "reactant"]',
          style: {
            "line-color": "#6688a8",
            "target-arrow-color": "#6688a8",
          },
        },
        {
          selector: 'edge[role = "product"]',
          style: {
            "line-color": "#72b99c",
            "target-arrow-color": "#72b99c",
          },
        },
        {
          selector: "edge:selected",
          style: {
            width: 3,
            "line-color": "#a9d9c5",
            "target-arrow-color": "#a9d9c5",
          },
        },
      ],
    });

    graphRef.current = graph;

    graph.on("tap", "node", (event) => {
      const node = event.target as NodeSingular;
      const nodeId = node.id();
      const currentTime = Date.now();

      const previousTap = lastTapRef.current;

      onNodeSelect(nodeId);

      if (
        previousTap &&
        previousTap.nodeId === nodeId &&
        currentTime - previousTap.time < 350
      ) {
        focusNode(graph, node);
        lastTapRef.current = null;
        return;
      }

      lastTapRef.current = {
        nodeId,
        time: currentTime,
      };
    });

    graph.on("tap", (event) => {
      if (event.target === graph) {
        onNodeSelect(null);
        lastTapRef.current = null;
      }
    });

    const resizeObserver = new ResizeObserver(() => {
      graph.resize();
    });

    resizeObserver.observe(container);

    return () => {
      resizeObserver.disconnect();
      graph.destroy();
      graphRef.current = null;
    };
  }, [scene, onNodeSelect]);

  useEffect(() => {
    const graph = graphRef.current;

    if (!graph) {
      return;
    }

    graph.nodes().unselect();

    if (selectedNodeIdentity) {
      const selected = graph.getElementById(
        selectedNodeIdentity,
      );

      if (selected.length > 0) {
        selected.select();
      }
    }
  }, [selectedNodeIdentity]);

  function handleFocusSelected(): void {
    const graph = graphRef.current;

    if (!graph || !selectedNodeIdentity) {
      return;
    }

    const node = graph.getElementById(
      selectedNodeIdentity,
    ) as NodeSingular;

    focusNode(graph, node);
  }

  function handleFitGraph(): void {
    graphRef.current?.animate(
      {
        fit: {
          eles: graphRef.current.elements(),
          padding: 70,
        },
      },
      {
        duration: 350,
        easing: "ease-in-out-cubic",
      },
    );
  }

  function handleResetView(): void {
    const graph = graphRef.current;

    if (!graph) {
      return;
    }

    graph.animate(
      {
        fit: {
          eles: graph.elements(),
          padding: 70,
        },
      },
      {
        duration: 350,
        easing: "ease-in-out-cubic",
      },
    );
  }

  return (
    <div className="pathway-graph-container">
      <div
        ref={containerRef}
        className="pathway-graph"
        role="application"
        aria-label="Interactive metabolic pathway graph"
      />

      <div className="pathway-graph-controls">
        <button
          type="button"
          onClick={handleFocusSelected}
          disabled={!selectedNodeIdentity}
          title="Focus selected node"
        >
          Focus
        </button>

        <button
          type="button"
          onClick={handleFitGraph}
          title="Fit entire pathway"
        >
          Fit
        </button>

        <button
          type="button"
          onClick={() => {
            const graph = graphRef.current;

            if (graph) {
              graph.zoom({
                level: Math.min(graph.zoom() * 1.2, 4),
                renderedPosition: {
                  x: graph.width() / 2,
                  y: graph.height() / 2,
                },
              });
            }
          }}
          title="Zoom in"
        >
          +
        </button>

        <button
          type="button"
          onClick={() => {
            const graph = graphRef.current;

            if (graph) {
              graph.zoom({
                level: Math.max(graph.zoom() / 1.2, 0.1),
                renderedPosition: {
                  x: graph.width() / 2,
                  y: graph.height() / 2,
                },
              });
            }
          }}
          title="Zoom out"
        >
          −
        </button>

        <button
          type="button"
          onClick={handleResetView}
          title="Reset pathway view"
        >
          Reset
        </button>
      </div>

      <div className="pathway-graph-legend">
        <span>
          <i className="legend-metabolite" />
          Metabolite
        </span>

        <span>
          <i className="legend-reaction" />
          Reaction
        </span>
      </div>
    </div>
  );
}
