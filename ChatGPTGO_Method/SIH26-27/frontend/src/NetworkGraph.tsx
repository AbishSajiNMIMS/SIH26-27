import { useEffect, useRef } from "react";
import cytoscape from "cytoscape";

function NetworkGraph() {
    const containerRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        if (!containerRef.current) return;

        const cy = cytoscape({
            container: containerRef.current,

            elements: [
                { data: { id: "P001" } },
                { data: { id: "P002" } },
                { data: { id: "P003" } },
                { data: { id: "P005" } },

                {
                    data: {
                        id: "e1",
                        source: "P001",
                        target: "P002"
                    }
                },

                {
                    data: {
                        id: "e2",
                        source: "P002",
                        target: "P003"
                    }
                },

                {
                    data: {
                        id: "e3",
                        source: "P003",
                        target: "P005"
                    }
                },

                {
                    data: {
                        id: "e4",
                        source: "P001",
                        target: "P005"
                    }
                }
            ],

            style: [
                {
                    selector: "node",
                    style: {
                        "label": "data(id)",
                        "width": 35,
                        "height": 35
                    }
                },
                {
                    selector: "edge",
                    style: {
                        "width": 2,
                        "curve-style": "bezier"
                    }
                }
            ],

            layout: {
                name: "cose"
            }
        });

        return () => {
            cy.destroy();
        };

    }, []);

    return (
        <div
            ref={containerRef}
            style={{
                width: "100%",
                height: "600px"
            }}
        />
    );
}

export default NetworkGraph;