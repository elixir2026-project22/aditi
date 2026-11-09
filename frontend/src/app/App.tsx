import { useEffect, useState } from "react";

import type {
  PathwaySceneNode,
  PathwaySceneResponse,
} from "../core/types";

import { useBackendStatus } from "../shared/hooks";

import {
  PathwayGraph,
  PathwayPropertiesPanel,
  PathwayExplorerPanel,
  SBMLImportPanel,
} from "../modules/pathways/components";

import "./App.css";

type ModuleId = "pathways" | "alignment" | "structure";

interface ApplicationModule {
  id: ModuleId;
  name: string;
  subtitle: string;
  icon: string;
  description: string;
}

const modules: ApplicationModule[] = [
  {
    id: "pathways",
    name: "Pathway Maps",
    subtitle: "Metabolic Networks",
    icon: "⌘",
    description:
      "Explore metabolic reactions, metabolites, and biological pathways.",
  },
  {
    id: "alignment",
    name: "Sequence Alignment",
    subtitle: "Multiple Sequence Analysis",
    icon: "≋",
    description:
      "Compare biological sequences and investigate conservation patterns.",
  },
  {
    id: "structure",
    name: "Protein Structure",
    subtitle: "Molecular Visualization",
    icon: "⬡",
    description:
      "Explore molecular structures and connect sequence information to 3D models.",
  },
];

function App() {
  const [activeModule, setActiveModule] =
    useState<ModuleId>("pathways");

  const [pathwayScene, setPathwayScene] =
    useState<PathwaySceneResponse | null>(null);

  const [selectedNodeIdentity, setSelectedNodeIdentity] =
    useState<string | null>(null);

  const [isVisualizationFullscreen, setIsVisualizationFullscreen] =
    useState(false);

  const backend = useBackendStatus();

  useEffect(() => {
    if (!isVisualizationFullscreen) {
      return;
    }

    function handleKeyDown(event: KeyboardEvent): void {
      if (event.key === "Escape") {
        setIsVisualizationFullscreen(false);
      }
    }

    window.addEventListener("keydown", handleKeyDown);

    return () => {
      window.removeEventListener("keydown", handleKeyDown);
    };
  }, [isVisualizationFullscreen]);

  const selectedModule = modules.find(
    (module) => module.id === activeModule,
  )!;

  const statusInformation = {
    connecting: {
      label: "CONNECTING",
      title: "Connecting to Backend",
      description: "Checking local API",
      color: "#d6ae68",
    },
    online: {
      label: "BACKEND ONLINE",
      title: "Backend Connected",
      description: "Aditi API is responding",
      color: "#72b99c",
    },
    offline: {
      label: "BACKEND OFFLINE",
      title: "Backend Unavailable",
      description: "Check the Python API server",
      color: "#d97878",
    },
  }[backend.status];

  function handleModuleChange(moduleId: ModuleId): void {
    setActiveModule(moduleId);
    setIsVisualizationFullscreen(false);
  }

  function handlePathwayImported(
    scene: PathwaySceneResponse,
  ): void {
    setPathwayScene(scene);
    setSelectedNodeIdentity(null);
  }

  return (
    <div
      className={`application ${isVisualizationFullscreen
          ? "visualization-fullscreen"
          : ""
        }`}
    >
      <aside className="sidebar">
        <div className="brand">
          <div className="brand-symbol">A</div>

          <div className="brand-content">
            <span className="brand-name">ADITI</span>
            <span className="brand-caption">
              Biological Intelligence
            </span>
          </div>
        </div>

        <div className="sidebar-divider" />

        <div className="navigation-heading">
          WORKSPACES
        </div>

        <nav className="module-navigation">
          {modules.map((module) => (
            <button
              key={module.id}
              type="button"
              className={`module-button ${activeModule === module.id ? "active" : ""
                }`}
              onClick={() => handleModuleChange(module.id)}
              aria-current={
                activeModule === module.id ? "page" : undefined
              }
            >
              <span className="module-icon">{module.icon}</span>

              <span className="module-labels">
                <span className="module-name">
                  {module.name}
                </span>

                <span className="module-subtitle">
                  {module.subtitle}
                </span>
              </span>

              {activeModule === module.id && (
                <span className="active-indicator" />
              )}
            </button>
          ))}
        </nav>

        <div className="sidebar-bottom">
          <div className="system-status">
            <span
              className="status-indicator"
              style={{
                backgroundColor: statusInformation.color,
                boxShadow: `0 0 9px ${statusInformation.color}55`,
              }}
            />

            <div>
              <span className="status-title">
                {statusInformation.title}
              </span>

              <span className="status-description">
                {statusInformation.description}
              </span>
            </div>
          </div>

          <div className="sidebar-footer">
            ADITI <span>·</span> VERSION 0.1.0
          </div>
        </div>
      </aside>

      <main className="main-content">
        <header className="topbar">
          <div className="breadcrumb">
            <span>Workspace</span>
            <span className="breadcrumb-separator">/</span>
            <strong>{selectedModule.name}</strong>
          </div>

          <div className="topbar-right">
            <div className="environment-label">
              <span
                className="environment-dot"
                style={{
                  backgroundColor: statusInformation.color,
                  boxShadow: `0 0 9px ${statusInformation.color}55`,
                }}
              />

              {statusInformation.label}
            </div>

            <div className="user-avatar">A</div>
          </div>
        </header>

        <section className="workspace">
          <div className="workspace-heading">
            <div>
              <div className="eyebrow">
                ADITI / BIOLOGICAL WORKSPACE
              </div>

              <h1>{selectedModule.name}</h1>

              <p className="workspace-description">
                {selectedModule.description}
              </p>
            </div>

            <div className="workspace-actions">
              <span className="module-version">
                MODULE 01
              </span>
            </div>
          </div>

          {activeModule === "pathways" && (
            <PathwayWorkspace
              availableLayouts={backend.availableLayouts}
              pathwayScene={pathwayScene}
              selectedNodeIdentity={selectedNodeIdentity}
              onNodeSelect={setSelectedNodeIdentity}
              onPathwayImported={handlePathwayImported}
              isFullscreen={isVisualizationFullscreen}
              onToggleFullscreen={() =>
                setIsVisualizationFullscreen((current) => !current)
              }
            />
          )}

          {activeModule === "alignment" && (
            <ModulePlaceholder
              title="Sequence Alignment"
              description="The sequence alignment workspace will be implemented as an independent biological module."
              icon="≋"
            />
          )}

          {activeModule === "structure" && (
            <ModulePlaceholder
              title="Protein Structure"
              description="The molecular structure workspace will be implemented as an independent biological module."
              icon="⬡"
            />
          )}
        </section>
      </main>
    </div>
  );
}

interface PathwayWorkspaceProps {
  availableLayouts: string[];
  pathwayScene: PathwaySceneResponse | null;
  selectedNodeIdentity: string | null;
  onNodeSelect: (identity: string | null) => void;
  onPathwayImported: (scene: PathwaySceneResponse) => void;
  isFullscreen: boolean;
  onToggleFullscreen: () => void;
}

function PathwayWorkspace({
  availableLayouts,
  pathwayScene,
  selectedNodeIdentity,
  onNodeSelect,
  onPathwayImported,
  isFullscreen,
  onToggleFullscreen,
}: PathwayWorkspaceProps) {
  const [isExplorerOpen, setIsExplorerOpen] = useState(false);
  const [isPropertiesOpen, setIsPropertiesOpen] = useState(false);

  const selectedNode: PathwaySceneNode | null =
    pathwayScene?.nodes.find(
      (node) => node.identity === selectedNodeIdentity,
    ) ?? null;

  function handleNodeSelect(identity: string): void {
    onNodeSelect(identity);
    setIsPropertiesOpen(true);
  }

  return (
    <>
      <div className="pathway-workspace">
        <div className="workspace-toolbar">
          <div className="toolbar-left">
            <span className="toolbar-label">
              {isFullscreen
                ? "ADITI / FULL-SCREEN VISUALIZATION"
                : "VISUALIZATION CANVAS"}
            </span>

            <span className="toolbar-divider" />

            <span className="toolbar-context">
              {pathwayScene
                ? "Pathway visualization"
                : "No pathway loaded"}
            </span>
          </div>

          <div className="toolbar-right">
            {pathwayScene && (
              <>
                <button
                  type="button"
                  className={`visualization-mode-button ${isExplorerOpen ? "panel-active" : ""
                    }`}
                  onClick={() =>
                    setIsExplorerOpen((current) => !current)
                  }
                  aria-pressed={isExplorerOpen}
                  title="Toggle pathway explorer"
                >
                  Explorer
                </button>

                <button
                  type="button"
                  className={`visualization-mode-button ${isPropertiesOpen ? "panel-active" : ""
                    }`}
                  onClick={() =>
                    setIsPropertiesOpen((current) => !current)
                  }
                  aria-pressed={isPropertiesOpen}
                  title="Toggle node properties"
                >
                  Properties
                </button>
              </>
            )}

            <span className="canvas-mode">2D GRAPH</span>

            <button
              type="button"
              className="visualization-mode-button"
              onClick={onToggleFullscreen}
              aria-label={
                isFullscreen
                  ? "Exit full-screen visualization"
                  : "Enter full-screen visualization"
              }
              title={
                isFullscreen
                  ? "Exit full screen (Esc)"
                  : "Enter full screen"
              }
            >
              {isFullscreen ? (
                <>
                  <span aria-hidden="true">↙</span>
                  <span>Exit</span>
                </>
              ) : (
                <>
                  <span aria-hidden="true">⛶</span>
                  <span>Expand</span>
                </>
              )}
            </button>
          </div>
        </div>

        <div className="visualization-canvas">
          <div className="canvas-grid" />

          {pathwayScene ? (
            <>
              <PathwayGraph
                scene={pathwayScene}
                selectedNodeIdentity={selectedNodeIdentity}
                onNodeSelect={onNodeSelect}
              />

              <PathwayExplorerPanel
                scene={pathwayScene}
                selectedNodeIdentity={selectedNodeIdentity}
                onNodeSelect={handleNodeSelect}
                isOpen={isExplorerOpen}
                onClose={() => setIsExplorerOpen(false)}
              />

              <PathwayPropertiesPanel
                scene={pathwayScene}
                selectedNode={selectedNode}
                onNodeSelect={handleNodeSelect}
                isOpen={isPropertiesOpen}
                onClose={() => setIsPropertiesOpen(false)}
              />
            </>
          ) : (
            <div className="canvas-empty-state">
              <div className="empty-state-symbol">
                <svg
                  viewBox="0 0 64 64"
                  fill="none"
                  xmlns="http://www.w3.org/2000/svg"
                  aria-hidden="true"
                >
                  <circle
                    cx="32"
                    cy="13"
                    r="6"
                    stroke="currentColor"
                    strokeWidth="1.5"
                  />
                  <circle
                    cx="13"
                    cy="48"
                    r="6"
                    stroke="currentColor"
                    strokeWidth="1.5"
                  />
                  <circle
                    cx="51"
                    cy="48"
                    r="6"
                    stroke="currentColor"
                    strokeWidth="1.5"
                  />
                  <path
                    d="M29 19L16 42M35 19L48 42M19 48H45"
                    stroke="currentColor"
                    strokeWidth="1.5"
                    strokeLinecap="round"
                  />
                  <circle
                    cx="32"
                    cy="32"
                    r="4"
                    fill="currentColor"
                  />
                </svg>
              </div>

              <h2>Pathway canvas is ready</h2>

              <p>
                Import a biological pathway to begin exploring
                its metabolites, reactions, and connections.
              </p>

              <span className="canvas-status">
                AWAITING PATHWAY DATA
              </span>
            </div>
          )}

          <div className="canvas-coordinate">
            CANVAS · 2D
          </div>
        </div>

        <div className="workspace-information">
          <div className="information-item">
            <span className="information-label">NODES</span>
            <span className="information-value">
              {pathwayScene?.nodes.length ?? "—"}
            </span>
          </div>

          <div className="information-item">
            <span className="information-label">EDGES</span>
            <span className="information-value">
              {pathwayScene?.edges.length ?? "—"}
            </span>
          </div>

          <div className="information-item">
            <span className="information-label">
              AVAILABLE LAYOUTS
            </span>
            <span className="information-value">
              {availableLayouts.join(", ") || "Loading..."}
            </span>
          </div>

          <div className="information-item">
            <span className="information-label">
              DATA SOURCE
            </span>
            <span className="information-value">
              SBML / Backend API
            </span>
          </div>
        </div>
      </div>

      <div className="pathway-import-section">
        <SBMLImportPanel
          availableLayouts={availableLayouts}
          onImported={onPathwayImported}
        />
      </div>
    </>
  );
}

interface ModulePlaceholderProps {
  title: string;
  description: string;
  icon: string;
}

function ModulePlaceholder({
  title,
  description,
  icon,
}: ModulePlaceholderProps) {
  return (
    <div className="module-placeholder">
      <div className="placeholder-icon">{icon}</div>

      <h2>{title}</h2>

      <p>{description}</p>

      <span className="placeholder-status">
        MODULE FOUNDATION PENDING
      </span>
    </div>
  );
}

export default App;