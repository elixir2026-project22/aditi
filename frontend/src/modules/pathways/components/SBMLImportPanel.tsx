import { useRef, useState } from "react";

import { ApiError } from "../../../core/api";
import type {
  PathwayLayoutId,
  PathwaySceneResponse,
} from "../../../core/types";
import { pathwayApi } from "../services";

import "./SBMLImportPanel.css";

interface SBMLImportPanelProps {
  availableLayouts: string[];
  onImported: (scene: PathwaySceneResponse) => void;
}

type ImportStatus = "idle" | "loading" | "success" | "error";

const SUPPORTED_LAYOUTS: PathwayLayoutId[] = [
  "hierarchical",
  "force-directed",
];

function isSupportedLayout(
  value: string,
): value is PathwayLayoutId {
  return SUPPORTED_LAYOUTS.includes(value as PathwayLayoutId);
}

function getErrorMessage(error: unknown): string {
  if (error instanceof ApiError) {
    if (error.status === 422) {
      return `Invalid SBML document: ${error.message}`;
    }

    if (error.status === 400) {
      return `Invalid visualization request: ${error.message}`;
    }

    if (error.isNetworkError) {
      return "Unable to reach the Aditi backend. Check that the Python API server is running.";
    }

    return error.message;
  }

  if (error instanceof Error) {
    return error.message;
  }

  return "An unexpected error occurred while importing the SBML document.";
}

export function SBMLImportPanel({
  availableLayouts,
  onImported,
}: SBMLImportPanelProps) {
  const fileInputRef = useRef<HTMLInputElement>(null);

  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [layoutId, setLayoutId] =
    useState<PathwayLayoutId>("hierarchical");

  const [status, setStatus] = useState<ImportStatus>("idle");
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const [successMessage, setSuccessMessage] = useState<string | null>(
    null,
  );

  const supportedLayouts = availableLayouts.filter(
    isSupportedLayout,
  );

  const effectiveLayout =
    supportedLayouts.includes(layoutId)
      ? layoutId
      : supportedLayouts[0] ?? "hierarchical";

  function handleFileChange(
    event: React.ChangeEvent<HTMLInputElement>,
  ): void {
    const file = event.target.files?.[0] ?? null;

    setSelectedFile(file);
    setErrorMessage(null);
    setSuccessMessage(null);
    setStatus("idle");
  }

  function handleRemoveFile(): void {
    setSelectedFile(null);
    setErrorMessage(null);
    setSuccessMessage(null);
    setStatus("idle");

    if (fileInputRef.current) {
      fileInputRef.current.value = "";
    }
  }

  async function handleImport(): Promise<void> {
    if (!selectedFile || status === "loading") {
      return;
    }

    if (supportedLayouts.length === 0) {
      setErrorMessage(
        "No supported pathway layouts are currently available from the backend.",
      );
      setStatus("error");
      return;
    }

    setStatus("loading");
    setErrorMessage(null);
    setSuccessMessage(null);

    try {
      const scene = await pathwayApi.importSBML(
        selectedFile,
        effectiveLayout,
      );

      onImported(scene);

      setStatus("success");
      setSuccessMessage(
        `Successfully imported ${selectedFile.name}.`,
      );
    } catch (error) {
      setStatus("error");
      setErrorMessage(getErrorMessage(error));
    }
  }

  return (
    <section className="sbml-import-panel">
      <div className="sbml-panel-heading">
        <div>
          <div className="sbml-eyebrow">BIOLOGICAL DATA IMPORT</div>
          <h2>Import pathway</h2>
          <p>
            Load a Systems Biology Markup Language document to
            generate a metabolic pathway visualization.
          </p>
        </div>

        <div className="sbml-file-icon">
          <svg
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="1.5"
            strokeLinecap="round"
            strokeLinejoin="round"
            aria-hidden="true"
          >
            <path d="M13 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V9z" />
            <path d="M13 2v7h7" />
            <path d="M12 18v-6" />
            <path d="m9 15 3-3 3 3" />
          </svg>
        </div>
      </div>

      <div className="sbml-form">
        <div className="sbml-field">
          <label className="sbml-field-label" htmlFor="sbml-file">
            SBML DOCUMENT
          </label>

          <input
            ref={fileInputRef}
            id="sbml-file"
            className="sbml-file-input"
            type="file"
            accept=".xml,.sbml,application/sbml+xml,application/xml,text/xml"
            onChange={handleFileChange}
            disabled={status === "loading"}
          />

          {selectedFile ? (
            <div className="sbml-selected-file">
              <div className="sbml-selected-file-icon">XML</div>

              <div className="sbml-file-details">
                <span className="sbml-file-name">
                  {selectedFile.name}
                </span>

                <span className="sbml-file-size">
                  {(selectedFile.size / 1024).toFixed(1)} KB
                </span>
              </div>

              <button
                type="button"
                className="sbml-remove-button"
                onClick={handleRemoveFile}
                disabled={status === "loading"}
                aria-label="Remove selected file"
              >
                ×
              </button>
            </div>
          ) : (
            <label
              className="sbml-dropzone"
              htmlFor="sbml-file"
            >
              <span className="sbml-dropzone-symbol">+</span>
              <span className="sbml-dropzone-title">
                Choose an SBML file
              </span>
              <span className="sbml-dropzone-description">
                XML or SBML document
              </span>
            </label>
          )}
        </div>

        <div className="sbml-field">
          <label
            className="sbml-field-label"
            htmlFor="sbml-layout"
          >
            VISUALIZATION LAYOUT
          </label>

          <select
            id="sbml-layout"
            className="sbml-layout-select"
            value={effectiveLayout}
            onChange={(event) => {
              if (isSupportedLayout(event.target.value)) {
                setLayoutId(event.target.value);
              }
            }}
            disabled={
              status === "loading" ||
              supportedLayouts.length === 0
            }
          >
            {supportedLayouts.map((layout) => (
              <option key={layout} value={layout}>
                {layout === "hierarchical"
                  ? "Hierarchical"
                  : "Force Directed"}
              </option>
            ))}
          </select>
        </div>

        <button
          type="button"
          className="sbml-import-button"
          onClick={() => void handleImport()}
          disabled={
            !selectedFile ||
            status === "loading" ||
            supportedLayouts.length === 0
          }
        >
          {status === "loading" ? (
            <>
              <span className="sbml-spinner" />
              Importing pathway...
            </>
          ) : (
            <>
              <span>Import pathway</span>
              <span>→</span>
            </>
          )}
        </button>
      </div>

      {status === "error" && errorMessage && (
        <div className="sbml-feedback sbml-feedback-error" role="alert">
          <strong>Import failed</strong>
          <span>{errorMessage}</span>
        </div>
      )}

      {status === "success" && successMessage && (
        <div
          className="sbml-feedback sbml-feedback-success"
          role="status"
        >
          <strong>Import successful</strong>
          <span>{successMessage}</span>
        </div>
      )}

      <div className="sbml-panel-footer">
        <span>FORMAT: SBML CORE XML</span>
        <span>PROCESSING: LOCAL BACKEND</span>
      </div>
    </section>
  );
}