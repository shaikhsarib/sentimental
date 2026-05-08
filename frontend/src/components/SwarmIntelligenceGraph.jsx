import React, { useMemo, useRef, useEffect, useState } from 'react';
import ForceGraph2D from 'react-force-graph-2d';
import ForceGraph3D from 'react-force-graph-3d';
import { buildClusterGraph, buildSubgraph, DEFAULT_MAX_VISIBLE_NODES } from '../utils/graphLod';

export default function SwarmIntelligenceGraph({ graphData, totalAgents, pins = [], pinEvidence = {} }) {
  const fgRef = useRef();
  const [clusterMode, setClusterMode] = useState(true);
  const [useWebGL, setUseWebGL] = useState(true);
  const [activeClusterId, setActiveClusterId] = useState(null);
  const [autoExpand, setAutoExpand] = useState(true);
  const autoExpandRef = useRef(false);
  const hoveredRef = useRef(null);
  const [tooltip, setTooltip] = useState(null);

  // Color mapping based on Tier (Blueprint Page 30)
  const TIER_COLORS = {
    1: '#60a5fa', // Blue (Executive)
    2: '#34d399', // Emerald (Specialist)
    3: '#94a3b8'  // Slate (Population)
  };

  // Emotion mapping for node 'glow' or specific sub-colors
  const EMOTION_COLORS = {
    aggressive: '#f87171', // Red
    cautious: '#fbbf24',   // Amber
    optimistic: '#60a5fa', // Blue
    pessimistic: '#818cf8', // Indigo
    neutral: '#94a3b8'     // Slate
  };

  // Limit nodes for rendering performance if needed, but the user wants 'density'
  // We'll use the provided graph but ensure it looks premium
  const processedData = useMemo(() => {
    if (!graphData) return { nodes: [], links: [] };
    
    return {
      nodes: graphData.nodes.map(node => ({
        ...node,
        val: node.tier === 1 ? 4 : (node.tier === 2 ? 2 : 1), // Size based on tier
        color: TIER_COLORS[node.tier] || '#94a3b8'
      })),
      links: graphData.edges.map(edge => ({
        source: edge.source,
        target: edge.target,
        value: edge.weight,
        color: 'rgba(255, 255, 255, 0.05)' // Subtle links for density look
      }))
    };
  }, [graphData]);

  const clusterKey = useMemo(() => (node) => {
    const tier = node.tier || 3;
    const domain = node.domain || 'GENERAL';
    return {
      key: `tier-${tier}-${domain}`,
      label: `Tier ${tier} // ${domain}`,
      color: TIER_COLORS[tier] || '#94a3b8'
    };
  }, []);

  const clusterGraph = useMemo(() => {
    return buildClusterGraph(processedData.nodes, processedData.links, clusterKey);
  }, [processedData, clusterKey]);

  const largestClusterId = useMemo(() => {
    let topId = null;
    let maxCount = 0;
    Object.values(clusterGraph.clusters).forEach(cluster => {
      if (cluster.memberCount > maxCount) {
        maxCount = cluster.memberCount;
        topId = cluster.id;
      }
    });
    return topId;
  }, [clusterGraph]);

  const shouldCluster = clusterMode && processedData.nodes.length > DEFAULT_MAX_VISIBLE_NODES;
  const activeCluster = activeClusterId ? clusterGraph.clusters[activeClusterId] : null;

  const activeGraph = useMemo(() => {
    if (activeCluster) {
      return buildSubgraph(processedData.nodes, processedData.links, activeCluster.members);
    }
    if (shouldCluster) {
      return clusterGraph.graph;
    }
    return processedData;
  }, [processedData, shouldCluster, activeCluster, clusterGraph]);

  useEffect(() => {
    if (fgRef.current) {
      // Configure physics for 'Million-Agent' density feel
      fgRef.current.d3Force('charge').strength(-20);
      fgRef.current.d3Force('link').distance(30);
    }
  }, [activeGraph]);

  const pinnedNodeIds = useMemo(() => {
    if (!pins.length) return new Set();
    const normalizedPins = pins.map(pin => String(pin).toLowerCase());
    const matches = processedData.nodes.filter(node => {
      const label = String(node.label || node.name || node.id || '').toLowerCase();
      return normalizedPins.some(pin => label.includes(pin));
    });
    return new Set(matches.map(node => node.id));
  }, [pins, processedData]);

  const pinnedVisibleNodes = useMemo(() => {
    if (!pinnedNodeIds.size) return [];
    return activeGraph.nodes.filter(node => pinnedNodeIds.has(node.id));
  }, [activeGraph, pinnedNodeIds]);

  const pinNodeMap = useMemo(() => {
    if (!pins.length) return new Map();
    const map = new Map();
    pins.forEach((pin) => {
      const target = pinnedVisibleNodes.find((node) => {
        const label = String(node.label || node.name || node.id || '').toLowerCase();
        return label.includes(String(pin).toLowerCase());
      });
      if (target) {
        map.set(pin, target);
      }
    });
    return map;
  }, [pins, pinnedVisibleNodes]);

  const evidenceLookup = useMemo(() => {
    const map = new Map();
    Object.entries(pinEvidence || {}).forEach(([key, value]) => {
      map.set(String(key).toLowerCase(), value);
    });
    return map;
  }, [pinEvidence]);

  const findPinMatch = (node) => {
    if (!node) return null;
    const label = String(node.label || node.name || node.id || '').toLowerCase();
    return pins.find(pin => label.includes(String(pin).toLowerCase())) || null;
  };

  const updateTooltip = (node, positionOnly = false) => {
    if (!node) {
      if (!positionOnly) setTooltip(null);
      return;
    }
    const pinMatch = findPinMatch(node);
    if (!pinMatch) {
      if (!positionOnly) setTooltip(null);
      return;
    }
    const coords = fgRef.current?.graph2ScreenCoords
      ? fgRef.current.graph2ScreenCoords(node.x, node.y, node.z || 0)
      : null;
    const pos = coords ? { x: coords.x + 12, y: coords.y + 12 } : { x: 20, y: 20 };

    if (positionOnly) {
      setTooltip(prev => prev ? { ...prev, x: pos.x, y: pos.y } : prev);
      return;
    }

    const evidence = evidenceLookup.get(String(pinMatch).toLowerCase()) || [];
    setTooltip({
      label: node.label || node.name || node.id,
      pin: pinMatch,
      evidence,
      x: pos.x,
      y: pos.y
    });
  };

  const focusNode = (node) => {
    if (!node || !fgRef.current || node.x === undefined || node.y === undefined) return;
    if (fgRef.current.centerAt) {
      fgRef.current.centerAt(node.x, node.y, 800);
      fgRef.current.zoom(2.5, 800);
      return;
    }
    if (fgRef.current.cameraPosition) {
      fgRef.current.cameraPosition({ x: node.x, y: node.y, z: 120 }, node, 800);
    }
  };

  const getZoomLevel = (event) => {
    if (event?.k) return event.k;
    if (event?.transform?.k) return event.transform.k;
    if (fgRef.current?.zoom) return fgRef.current.zoom();
    const camera = fgRef.current?.camera?.();
    if (camera?.position?.z) {
      return Math.min(4, Math.max(0.4, 200 / camera.position.z));
    }
    return null;
  };

  const handleAutoExpand = (zoomLevel) => {
    if (!autoExpand || !shouldCluster || !largestClusterId || zoomLevel === null) return;
    if (!activeClusterId && zoomLevel >= 2.2 && !autoExpandRef.current) {
      setActiveClusterId(largestClusterId);
      autoExpandRef.current = true;
    } else if (activeClusterId && zoomLevel <= 1.1 && autoExpandRef.current) {
      setActiveClusterId(null);
      autoExpandRef.current = false;
    }
  };

  if (!graphData) return null;

  const [activeThought, setActiveThought] = useState(null);

  useEffect(() => {
    // Periodic "Thought Bubbles" for visual interaction (Blueprint Page 34)
    const interval = setInterval(() => {
      if (activeGraph.nodes.length > 0) {
        const randomNode = activeGraph.nodes[Math.floor(Math.random() * activeGraph.nodes.length)];
        const thoughts = [
          "Analyzing narrative contagion...",
          "Validating tier-2 influence...",
          "Applying emotion physics...",
          "Synthesizing consensus...",
          "Checking SEIR propagation...",
          "Evaluating R0 risk..."
        ];
        setActiveThought({
          nodeId: randomNode.id,
          text: thoughts[Math.floor(Math.random() * thoughts.length)],
          x: randomNode.x,
          y: randomNode.y
        });
        
        // Hide after 3s
        setTimeout(() => setActiveThought(null), 3000);
      }
    }, 5000);
    return () => clearInterval(interval);
  }, [activeGraph]);

  const handleNodeClick = (node) => {
    if (node.isCluster) {
      setActiveClusterId(node.id);
      return;
    }
    focusNode(node);
  };

  const particleCount = activeGraph.nodes.length > 6000 ? 0 : 1;
  const linkWidth = (link) => {
    const weight = link.value || link.weight || 1;
    return Math.max(0.3, weight * 0.2);
  };

  return (
    <div className="swarm-graph-container relative w-full h-[600px] bg-[#050505] rounded-3xl overflow-hidden border border-white/10 shadow-2xl">
      <div className="graph-tools">
        <button
          type="button"
          className={`graph-chip ${clusterMode ? 'active' : ''}`}
          onClick={() => {
            setClusterMode((prev) => !prev);
            setActiveClusterId(null);
            autoExpandRef.current = false;
          }}
        >
          CLUSTERS
        </button>
        <button
          type="button"
          className={`graph-chip ${useWebGL ? 'active' : ''}`}
          onClick={() => setUseWebGL((prev) => !prev)}
        >
          WEBGL
        </button>
        <button
          type="button"
          className={`graph-chip ${autoExpand ? 'active' : ''}`}
          onClick={() => {
            setAutoExpand((prev) => !prev);
            autoExpandRef.current = false;
          }}
        >
          AUTO
        </button>
        {activeCluster && (
          <button
            type="button"
            className="graph-chip"
            onClick={() => setActiveClusterId(null)}
          >
            BACK
          </button>
        )}
        <span className="graph-chip muted">{activeGraph.nodes.length.toLocaleString()} visible</span>
      </div>
      {pins.length > 0 && (
        <div className="graph-pins">
          <div className="graph-pins-title">CITATION PINS</div>
          <div className="graph-pins-list">
            {pins.slice(0, 6).map((pin, index) => (
              <button
                key={`${pin}-${index}`}
                type="button"
                className="graph-pin"
                onClick={() => focusNode(pinNodeMap.get(pin))}
              >
                {pin}
              </button>
            ))}
          </div>
        </div>
      )}
      {tooltip && (
        <div
          className="graph-tooltip"
          style={{ left: tooltip.x, top: tooltip.y }}
        >
          <div className="graph-tooltip-title">{tooltip.pin}</div>
          <div className="graph-tooltip-label">{tooltip.label}</div>
          {tooltip.evidence.length > 0 && (
            <div className="graph-tooltip-body">
              {tooltip.evidence.map((line, index) => (
                <div key={index} className="graph-tooltip-line">{line}</div>
              ))}
            </div>
          )}
        </div>
      )}
      {/* Thought Bubble Overlay */}
      {activeThought && (
        <div 
          className="absolute z-20 pointer-events-none animate-bounce"
          style={{ 
            left: '50%', 
            top: '20%', 
            transform: 'translate(-50%, -50%)' 
          }}
        >
          <div className="bg-blue-600/90 text-white text-[10px] px-3 py-1.5 rounded-full font-mono border border-blue-400/50 shadow-lg backdrop-blur-md">
            {activeThought.text}
          </div>
        </div>
      )}
      <div className="absolute top-6 left-6 z-10 font-mono text-[10px] space-y-1">
        <div className="flex items-center gap-2">
          <span className="w-2 h-2 rounded-full bg-[#60a5fa]"></span>
          <span className="text-gray-400">EXECUTIVE TIER (LAYER 3)</span>
        </div>
        <div className="flex items-center gap-2">
          <span className="w-2 h-2 rounded-full bg-[#34d399]"></span>
          <span className="text-gray-400">SPECIALIST TIER (LAYER 2)</span>
        </div>
        <div className="flex items-center gap-2">
          <span className="w-2 h-2 rounded-full bg-[#94a3b8]"></span>
          <span className="text-gray-400">POPULATION SWARM (LAYER 1)</span>
        </div>
      </div>

      <div className="absolute bottom-6 right-6 z-10 text-right">
        <p className="text-[10px] font-mono text-gray-500 uppercase tracking-widest">Topology Status</p>
        <p className="text-xl font-bold text-blue-400">
          {(graphData.metadata?.node_count || processedData.nodes.length).toLocaleString()} NODES // {(graphData.metadata?.edge_count || processedData.links.length).toLocaleString()} EDGES
        </p>
      </div>
      {useWebGL ? (
        <ForceGraph3D
          ref={fgRef}
          graphData={activeGraph}
          backgroundColor="#050505"
          nodeLabel={(node) => node.label || node.name || node.id}
          nodeRelSize={4}
          nodeColor={(node) => node.color || '#94a3b8'}
          linkColor={() => 'rgba(255, 255, 255, 0.08)'}
          linkWidth={linkWidth}
          linkDirectionalParticles={particleCount}
          linkDirectionalParticleSpeed={(d) => (d.value || 1) * 0.01}
          linkDirectionalParticleWidth={1}
          linkDirectionalParticleColor={() => '#60a5fa'}
          onNodeClick={handleNodeClick}
          onNodeHover={(node) => {
            hoveredRef.current = node;
            updateTooltip(node);
          }}
          onEngineTick={() => {
            handleAutoExpand(getZoomLevel());
            if (hoveredRef.current) {
              updateTooltip(hoveredRef.current, true);
            }
          }}
        />
      ) : (
        <ForceGraph2D
          ref={fgRef}
          graphData={activeGraph}
          backgroundColor="#050505"
          nodeLabel={(node) => node.label || node.name || node.id}
          nodeRelSize={4}
          linkDirectionalParticles={particleCount}
          linkDirectionalParticleSpeed={(d) => (d.value || 1) * 0.01}
          linkDirectionalParticleWidth={1}
          linkDirectionalParticleColor={() => '#60a5fa'}
          linkColor={() => 'rgba(255, 255, 255, 0.08)'}
          onNodeClick={handleNodeClick}
          onNodeHover={(node) => {
            hoveredRef.current = node;
            updateTooltip(node);
          }}
          onZoomEnd={(event) => handleAutoExpand(getZoomLevel(event))}
          nodeCanvasObject={(node, ctx, globalScale) => {
            const label = node.label || node.name || node.id;
            const fontSize = 12 / globalScale;
            ctx.font = `${fontSize}px Inter`;

            const coreSize = node.isCluster ? node.val * 1.4 : node.val;
            const isPinned = pinnedNodeIds.has(node.id);

            // Draw Node Glow
            const gradient = ctx.createRadialGradient(node.x, node.y, 0, node.x, node.y, coreSize * 3);
            gradient.addColorStop(0, node.color || '#94a3b8');
            gradient.addColorStop(1, 'transparent');
            ctx.fillStyle = gradient;
            ctx.beginPath();
            ctx.arc(node.x, node.y, coreSize * 3, 0, 2 * Math.PI, false);
            ctx.fill();

            // Draw Core Node
            ctx.fillStyle = node.color || '#94a3b8';
            ctx.beginPath();
            ctx.arc(node.x, node.y, coreSize, 0, 2 * Math.PI, false);
            ctx.fill();

            if (isPinned) {
              ctx.strokeStyle = 'rgba(96, 165, 250, 0.9)';
              ctx.lineWidth = 2 / globalScale;
              ctx.beginPath();
              ctx.arc(node.x, node.y, coreSize + 3, 0, 2 * Math.PI, false);
              ctx.stroke();
            }

            if ((node.tier === 1 || node.isCluster) && globalScale > 1.2) {
              ctx.textAlign = 'center';
              ctx.textBaseline = 'middle';
              ctx.fillStyle = isPinned ? 'rgba(147, 197, 253, 0.9)' : 'rgba(255, 255, 255, 0.6)';
              ctx.fillText(label, node.x, node.y + 6);
            }
          }}
        />
      )}
    </div>
  );
}
