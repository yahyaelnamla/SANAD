"use client";

import { motion } from "framer-motion";
import { Loader2, Network, Search, ZoomIn, ZoomOut } from "lucide-react";
import { useEffect, useMemo, useState } from "react";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { useAuth } from "@/hooks/useAuth";
import { useTranslations } from "@/hooks/useTranslations";
import { localizeGraphEdge, localizeGraphNodeType } from "@/lib/domainLocalizations";
import { ApiClientError } from "@/services/apiClient";
import { fetchKnowledgeGraph, type KnowledgeGraphData } from "@/services/featuresService";

const NODE_COLORS: Record<string, string> = {
  quran: "#22C55E",
  hadith: "#FACC15",
  standard: "#3B82F6",
  institution: "#A855F7",
  topic: "#00E5FF",
  classical: "#14B8A6",
  fatwa: "#8B5CF6",
  concept: "#06B6D4",
  company: "#F97316",
  entity: "#64748B",
};

interface LayoutNode {
  id: string;
  label: string;
  type: string;
  x: number;
  y: number;
  vx: number;
  vy: number;
}

function runForceLayout(
  nodes: LayoutNode[],
  edges: { source: string; target: string }[],
  width: number,
  height: number,
  iterations = 80,
): LayoutNode[] {
  const positioned = [...nodes];
  const centerX = width / 2;
  const centerY = height / 2;

  for (let step = 0; step < iterations; step += 1) {
    for (const node of positioned) {
      node.vx += (centerX - node.x) * 0.002;
      node.vy += (centerY - node.y) * 0.002;
    }

    for (let i = 0; i < positioned.length; i += 1) {
      for (let j = i + 1; j < positioned.length; j += 1) {
        const a = positioned[i];
        const b = positioned[j];
        const dx = b.x - a.x;
        const dy = b.y - a.y;
        const dist = Math.max(Math.hypot(dx, dy), 1);
        const force = 1200 / (dist * dist);
        const fx = (dx / dist) * force;
        const fy = (dy / dist) * force;
        a.vx -= fx;
        a.vy -= fy;
        b.vx += fx;
        b.vy += fy;
      }
    }

    for (const edge of edges) {
      const source = positioned.find((n) => n.id === edge.source);
      const target = positioned.find((n) => n.id === edge.target);
      if (!source || !target) continue;
      const dx = target.x - source.x;
      const dy = target.y - source.y;
      const dist = Math.max(Math.hypot(dx, dy), 1);
      const force = (dist - 90) * 0.04;
      const fx = (dx / dist) * force;
      const fy = (dy / dist) * force;
      source.vx += fx;
      source.vy += fy;
      target.vx -= fx;
      target.vy -= fy;
    }

    for (const node of positioned) {
      node.vx *= 0.85;
      node.vy *= 0.85;
      node.x = Math.min(width - 40, Math.max(40, node.x + node.vx));
      node.y = Math.min(height - 40, Math.max(40, node.y + node.vy));
    }
  }

  return positioned;
}

export function KnowledgeGraphPanel() {
  const { t, locale } = useTranslations();
  const { accessToken } = useAuth();
  const [graph, setGraph] = useState<KnowledgeGraphData | null>(null);
  const [filter, setFilter] = useState("");
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [zoom, setZoom] = useState(1);

  useEffect(() => {
    if (!accessToken) {
      setLoading(false);
      return;
    }
    fetchKnowledgeGraph(accessToken, locale)
      .then(setGraph)
      .catch((err) => setError(err instanceof ApiClientError ? err.message : t("errors.generic")))
      .finally(() => setLoading(false));
  }, [accessToken, locale, t]);

  const layout = useMemo(() => {
    if (!graph) return { nodes: [], edges: [] };

    const width = 900;
    const height = 520;
    const seedNodes: LayoutNode[] = graph.nodes.map((node, index) => ({
      id: node.id,
      label: node.label,
      type: node.type,
      x: node.x * width,
      y: node.y * height,
      vx: 0,
      vy: 0,
    }));

    if (seedNodes.every((n, i) => graph.nodes[i]?.x === graph.nodes[0]?.x)) {
      seedNodes.forEach((node, index) => {
        const angle = (2 * Math.PI * index) / seedNodes.length;
        node.x = width / 2 + Math.cos(angle) * 180;
        node.y = height / 2 + Math.sin(angle) * 160;
      });
    }

    const laidOut = runForceLayout(seedNodes, graph.edges, width, height);
    return { nodes: laidOut, edges: graph.edges, width, height };
  }, [graph]);

  const filteredNodes = useMemo(() => {
    const query = filter.trim().toLowerCase();
    if (!query) return layout.nodes;
    return layout.nodes.filter(
      (node) => node.label.toLowerCase().includes(query) || node.type.toLowerCase().includes(query),
    );
  }, [layout.nodes, filter]);

  const selectedNode = layout.nodes.find((node) => node.id === selectedId) ?? null;
  const connectedEdges = graph?.edges.filter(
    (edge) => edge.source === selectedId || edge.target === selectedId,
  );

  if (loading) {
    return (
      <div className="flex justify-center py-20">
        <Loader2 className="h-6 w-6 animate-spin text-cyan-400" />
      </div>
    );
  }

  if (error) {
    return <p className="py-20 text-center text-destructive">{error}</p>;
  }

  return (
    <div className="mx-auto max-w-6xl space-y-4">
      <div className="flex flex-wrap items-center gap-2">
        <div className="relative flex-1">
          <Search className="pointer-events-none absolute start-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
          <Input
            value={filter}
            onChange={(e) => setFilter(e.target.value)}
            placeholder={t("knowledgeGraph.search")}
            className="ps-9"
          />
        </div>
        <Button type="button" variant="outline" size="icon" onClick={() => setZoom((z) => Math.min(2, z + 0.15))}>
          <ZoomIn className="h-4 w-4" />
        </Button>
        <Button type="button" variant="outline" size="icon" onClick={() => setZoom((z) => Math.max(0.6, z - 0.15))}>
          <ZoomOut className="h-4 w-4" />
        </Button>
      </div>

      <Card className="glass-card overflow-hidden">
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-lg">
            <Network className="h-5 w-5 text-cyan-400" />
            {t("knowledgeGraph.title")}
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="relative overflow-hidden rounded-xl border border-border/40 bg-background/40">
            <svg
              viewBox={`0 0 ${layout.width ?? 900} ${layout.height ?? 520}`}
              className="h-[min(70vh,560px)] w-full"
              style={{ transform: `scale(${zoom})`, transformOrigin: "center center" }}
            >
              <defs>
                <filter id="glow">
                  <feGaussianBlur stdDeviation="2" result="blur" />
                  <feMerge>
                    <feMergeNode in="blur" />
                    <feMergeNode in="SourceGraphic" />
                  </feMerge>
                </filter>
              </defs>

              {layout.edges.map((edge) => {
                const source = layout.nodes.find((node) => node.id === edge.source);
                const target = layout.nodes.find((node) => node.id === edge.target);
                if (!source || !target) return null;
                const visible =
                  filteredNodes.some((n) => n.id === source.id) &&
                  filteredNodes.some((n) => n.id === target.id);
                if (!visible) return null;
                const highlighted =
                  selectedId && (edge.source === selectedId || edge.target === selectedId);
                return (
                  <line
                    key={`${edge.source}-${edge.target}`}
                    x1={source.x}
                    y1={source.y}
                    x2={target.x}
                    y2={target.y}
                    stroke={highlighted ? "rgba(0,229,255,0.65)" : "rgba(0,229,255,0.22)"}
                    strokeWidth={highlighted ? 2.5 : 1.5}
                  />
                );
              })}

              {filteredNodes.map((node) => {
                const selected = selectedId === node.id;
                const dimmed = selectedId && selectedId !== node.id;
                const color = NODE_COLORS[node.type] ?? "#00E5FF";
                return (
                  <g
                    key={node.id}
                    onClick={() => setSelectedId(node.id)}
                    className="cursor-pointer"
                    opacity={dimmed ? 0.35 : 1}
                  >
                    <circle
                      cx={node.x}
                      cy={node.y}
                      r={selected ? 16 : 12}
                      fill={color}
                      filter={selected ? "url(#glow)" : undefined}
                    />
                    <text
                      x={node.x}
                      y={node.y + 26}
                      textAnchor="middle"
                      fontSize="11"
                      fill="currentColor"
                      className="pointer-events-none select-none"
                    >
                      {node.label.length > 28 ? `${node.label.slice(0, 28)}…` : node.label}
                    </text>
                  </g>
                );
              })}
            </svg>
          </div>
        </CardContent>
      </Card>

      {selectedNode && (
        <motion.div initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }}>
          <Card className="glass-card">
            <CardContent className="space-y-3 pt-6">
              <div className="flex items-center justify-between gap-3">
                <div>
                  <p className="text-lg font-semibold">{selectedNode.label}</p>
                  <p className="text-sm text-muted-foreground">
                    {t("knowledgeGraph.nodeType")}: {localizeGraphNodeType(selectedNode.type, locale)}
                  </p>
                </div>
                <Badge variant="outline">{localizeGraphNodeType(selectedNode.type, locale)}</Badge>
              </div>
              {connectedEdges && connectedEdges.length > 0 && (
                <div className="space-y-1 text-sm text-muted-foreground">
                  {connectedEdges.slice(0, 6).map((edge) => {
                    const peerId = edge.source === selectedId ? edge.target : edge.source;
                    const peer = layout.nodes.find((n) => n.id === peerId);
                    return (
                      <p key={`${edge.source}-${edge.target}`}>
                        {localizeGraphEdge(edge.label ?? "related", locale)} → {peer?.label ?? peerId}
                      </p>
                    );
                  })}
                </div>
              )}
            </CardContent>
          </Card>
        </motion.div>
      )}
    </div>
  );
}
