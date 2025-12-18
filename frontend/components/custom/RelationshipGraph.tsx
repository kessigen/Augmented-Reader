"use client";

import React, { useEffect, useState } from "react";
import { GraphCanvas, type GraphNode, type GraphEdge } from "reagraph";

type Props = { bookId: number };

export default function RelationshipGraph({ bookId }: Props) {
  const [nodes, setNodes] = useState<GraphNode[]>([]);
  const [edges, setEdges] = useState<GraphEdge[]>([]);

  useEffect(() => {
    fetch(`http://127.0.0.1:8000/api/books/${bookId}/graph/`)
      .then((r) => r.json())
      .then((j) => {
        setNodes(j.nodes || []);
        setEdges(j.edges || []);
      })
      .catch(() => {
        setNodes([]);
        setEdges([]);
      });
  }, [bookId]);

  return (
    <div className="w-[800px] h-[500px] bg-slate-50 rounded-lg shadow-inner overflow-hidden">
      <GraphCanvas
        nodes={nodes}
        edges={edges}
        labelType="all"
        edgeLabelPosition="inline"
        edgeArrowPosition="end"
        draggable
      />
    </div>
  );
}
