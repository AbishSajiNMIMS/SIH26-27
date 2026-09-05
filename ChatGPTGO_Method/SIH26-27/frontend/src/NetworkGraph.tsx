import { useEffect, useRef } from "react";
import cytoscape from "cytoscape";

type NetworkNode = {
  id: string;
  label: string;
  type: string;
};

type NetworkEdge = {
  source: string;
  target: string;
  type: string;
  duration_sec: number;
  timestamp: string;
  cell_tower: string;
};

type NetworkData = {
  nodes: NetworkNode[];
  edges: NetworkEdge[];
};

function NetworkGraph() {
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    let cy: cytoscape.Core | undefined;
    let cancelled = false;

    const loadNetwork = async () => {
      try {
        const response = await fetch(
          "http://127.0.0.1:8000/network"
        );

        if (!response.ok) {
          throw new Error("Failed to fetch network");
        }

        const data: NetworkData = await response.json();

        if (cancelled || !containerRef.current) {
          return;
        }

        cy = cytoscape({
          container: containerRef.current,

          elements: [
            ...data.nodes.map((node) => ({
              data: {
                id: node.id,
                label: node.label,
                type: node.type,
              },
            })),

            ...data.edges.map((edge, index) => ({
              data: {
                id: `edge-${index}`,
                source: edge.source,
                target: edge.target,
                type: edge.type,
                duration_sec: edge.duration_sec,
                timestamp: edge.timestamp,
                cell_tower: edge.cell_tower,
              },
            })),
          ],

          style: [
            {
              selector: "node",
              style: {
                label: "data(label)",
                "background-color": "#2563eb",
                color: "#ffffff",
                "text-valign": "center",
                "text-halign": "center",
                width: 40,
                height: 40,
                "font-size": 12,
              },
            },

            {
              selector: "edge",
              style: {
                width: 2,
                "line-color": "#94a3b8",
                "target-arrow-color": "#94a3b8",
                "target-arrow-shape": "triangle",
                "curve-style": "bezier",
              },
            },
          ],

          layout: {
            name: "cose",
            animate: false,
          },
        });
      } catch (error) {
        if (!cancelled) {
          console.error("Network loading error:", error);
        }
      }
    };

    loadNetwork();

    return () => {
      cancelled = true;
      if (cy) {
        cy.destroy();
      }
    };
  }, []);

  return (
    <div
      ref={containerRef}
      style={{
        width: "100%",
        height: "700px",
        border: "1px solid #ddd",
      }}
    />
  );
}

export default NetworkGraph;