
import { useMemo, useState } from "react";

import type {
  PathwaySceneNode,
  PathwaySceneResponse,
} from "../../../core/types";

import "./PathwayPanels.css";

interface PathwayExplorerPanelProps {
  scene: PathwaySceneResponse;
  selectedNodeIdentity: string | null;
  onNodeSelect: (identity: string) => void;
  isOpen: boolean;
  onClose: () => void;
}

interface PathwayPropertiesPanelProps {
  scene: PathwaySceneResponse;
  selectedNode: PathwaySceneNode | null;
  onNodeSelect: (identity: string) => void;
  isOpen: boolean;
  onClose: () => void;
}

export function PathwayExplorerPanel({
  scene,
  selectedNodeIdentity,
  onNodeSelect,
  isOpen,
  onClose,
}: PathwayExplorerPanelProps) {
  const [search, setSearch] = useState("");
  const [activeFilter, setActiveFilter] = useState<
    "all" | "metabolite" | "reaction"
  >("all");

  const filteredNodes = useMemo(() => {
    const query = search.trim().toLowerCase();

    return scene.nodes.filter((node) => {
      const matchesType =
        activeFilter === "all" ||
        node.node_type === activeFilter;

      const matchesSearch =
        query.length === 0 ||
        node.label.toLowerCase().includes(query) ||
        node.identity.toLowerCase().includes(query);

      return matchesType && matchesSearch;
    });
  }, [scene.nodes, search, activeFilter]);

  const metaboliteCount = scene.nodes.filter(
    (node) => node.node_type === "metabolite",
  ).length;

  const reactionCount = scene.nodes.filter(
    (node) => node.node_type === "reaction",
  ).length;

  return (
    <aside
      className={`pathway-side-panel pathway-explorer ${
        isOpen ? "panel-open" : "panel-closed"
      }`}
      aria-hidden={!isOpen}
    >
      <div className="pathway-panel-header">
        <div>
          <span className="pathway-panel-eyebrow">
            PATHWAY CONTENTS
          </span>
          <h3>Explorer</h3>
        </div>

        <button
          type="button"
          className="pathway-panel-close"
          onClick={onClose}
          aria-label="Close pathway explorer"
          title="Close explorer"
        >
          ×
        </button>
      </div>

      <div className="pathway-explorer-summary">
        <div>
          <strong>{metaboliteCount}</strong>
          <span>Metabolites</span>
        </div>

        <div>
          <strong>{reactionCount}</strong>
          <span>Reactions</span>
        </div>
      </div>

      <input
        className="pathway-explorer-search"
        type="search"
        placeholder="Search pathway..."
        value={search}
        onChange={(event) => setSearch(event.target.value)}
        aria-label="Search pathway nodes"
      />

      <div className="pathway-explorer-filters">
        {(["all", "metabolite", "reaction"] as const).map(
          (filter) => (
            <button
              key={filter}
              type="button"
              className={
                activeFilter === filter ? "active" : ""
              }
              onClick={() => setActiveFilter(filter)}
            >
              {filter === "all"
                ? "All"
                : filter === "metabolite"
                  ? "Metabolites"
                  : "Reactions"}
            </button>
          ),
        )}
      </div>

      <div className="pathway-explorer-list">
        {filteredNodes.length > 0 ? (
          filteredNodes.map((node) => (
            <button
              key={node.identity}
              type="button"
              className={`pathway-explorer-item ${
                selectedNodeIdentity === node.identity
                  ? "selected"
                  : ""
              }`}
              onClick={() => onNodeSelect(node.identity)}
            >
              <span
                className={`explorer-node-icon ${node.node_type}`}
              >
                {node.node_type === "metabolite" ? "M" : "R"}
              </span>

              <span className="explorer-node-labels">
                <strong>{node.label}</strong>
                <small>{node.identity}</small>
              </span>

              {selectedNodeIdentity === node.identity && (
                <span className="explorer-selected-indicator" />
              )}
            </button>
          ))
        ) : (
          <div className="pathway-explorer-empty">
            <span>No matching nodes</span>
            <small>Try another search or filter.</small>
          </div>
        )}
      </div>

      <div className="pathway-panel-footer">
        Showing {filteredNodes.length} of {scene.nodes.length} nodes
      </div>
    </aside>
  );
}

export function PathwayPropertiesPanel({
  scene,
  selectedNode,
  onNodeSelect,
  isOpen,
  onClose,
}: PathwayPropertiesPanelProps) {
  const connectedNodes = useMemo(() => {
    if (!selectedNode) {
      return [];
    }

    return scene.edges
      .filter(
        (edge) =>
          edge.source_identity === selectedNode.identity ||
          edge.target_identity === selectedNode.identity,
      )
      .map((edge, index) => {
        const isOutgoing =
          edge.source_identity === selectedNode.identity;

        const otherIdentity = isOutgoing
          ? edge.target_identity
          : edge.source_identity;

        const otherNode = scene.nodes.find(
          (node) => node.identity === otherIdentity,
        );

        return {
          key: `${otherIdentity}-${index}`,
          identity: otherIdentity,
          label: otherNode?.label ?? otherIdentity,
          nodeType: otherNode?.node_type ?? "unknown",
          direction: isOutgoing ? "Outgoing" : "Incoming",
          role: edge.role,
          coefficient: edge.coefficient,
        };
      });
  }, [scene, selectedNode]);

  return (
    <aside
      className={`pathway-side-panel pathway-properties ${
        isOpen ? "panel-open" : "panel-closed"
      }`}
      aria-hidden={!isOpen}
    >
      <div className="pathway-panel-header">
        <div>
          <span className="pathway-panel-eyebrow">
            NODE INSPECTOR
          </span>
          <h3>Properties</h3>
        </div>

        <button
          type="button"
          className="pathway-panel-close"
          onClick={onClose}
          aria-label="Close properties panel"
          title="Close properties"
        >
          ×
        </button>
      </div>

      {selectedNode ? (
        <>
          <div className="property-node-heading">
            <span
              className={`explorer-node-icon large ${selectedNode.node_type}`}
            >
              {selectedNode.node_type === "metabolite" ? "M" : "R"}
            </span>

            <div>
              <span className="property-node-type">
                {selectedNode.node_type}
              </span>
              <h4>{selectedNode.label}</h4>
            </div>
          </div>

          <div className="property-section">
            <span className="property-section-title">
              IDENTIFICATION
            </span>

            <div className="property-row">
              <span>Identity</span>
              <strong>{selectedNode.identity}</strong>
            </div>

            <div className="property-row">
              <span>Node type</span>
              <strong>{selectedNode.node_type}</strong>
            </div>

            <div className="property-row">
              <span>Connections</span>
              <strong>{connectedNodes.length}</strong>
            </div>
          </div>

          <div className="property-section">
            <span className="property-section-title">
              CONNECTED NODES
            </span>

            {connectedNodes.length > 0 ? (
              <div className="property-connections">
                {connectedNodes.map((connection) => (
                  <button
                    type="button"
                    className="property-connection"
                    key={connection.key}
                    onClick={() =>
                      onNodeSelect(connection.identity)
                    }
                    title={`Navigate to ${connection.label}`}
                    aria-label={`Select connected node ${connection.label}`}
                  >
                    <span
                      className={`explorer-node-icon ${connection.nodeType}`}
                    >
                      {connection.nodeType === "metabolite"
                        ? "M"
                        : "R"}
                    </span>

                    <span className="property-connection-content">
                      <strong>{connection.label}</strong>
                      <small>
                        {connection.direction} · {connection.role}
                        {connection.coefficient !== "1"
                          ? ` · coefficient ${connection.coefficient}`
                          : ""}
                      </small>
                    </span>

                    <span
                      className="property-connection-arrow"
                      aria-hidden="true"
                    >
                      →
                    </span>
                  </button>
                ))}
              </div>
            ) : (
              <div className="property-empty">
                No connected nodes were found.
              </div>
            )}
          </div>
        </>
      ) : (
        <div className="property-selection-empty">
          <div className="property-empty-symbol">⌖</div>
          <strong>No node selected</strong>
          <p>
            Select a metabolite or reaction in the graph or
            pathway explorer to inspect its properties.
          </p>
        </div>
      )}
    </aside>
  );
}
