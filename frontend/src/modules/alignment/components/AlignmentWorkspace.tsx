
import { useState } from "react";

import { alignmentApi } from "../services";
import type {
  AlignmentGapModel,
  AlignmentScoringMethod,
  AlignmentType,
  SequenceAlphabet,
  SequenceAlignmentResponse,
} from "../../../core/types";

import "./AlignmentWorkspace.css";

export function AlignmentWorkspace() {
  const [firstName, setFirstName] = useState("Sequence 1");
  const [secondName, setSecondName] = useState("Sequence 2");
  const [firstResidues, setFirstResidues] = useState("");
  const [secondResidues, setSecondResidues] = useState("");

  const [alphabet, setAlphabet] = useState<SequenceAlphabet>("dna");
  const [alignmentType, setAlignmentType] =
    useState<AlignmentType>("global");

  const [scoringMethod, setScoringMethod] =
    useState<AlignmentScoringMethod>("simple");
  const [matchScore, setMatchScore] = useState(2);
  const [mismatchScore, setMismatchScore] = useState(-1);

  const [gapModel, setGapModel] = useState<AlignmentGapModel>("linear");
  const [gapPenalty, setGapPenalty] = useState(-2);
  const [gapOpenPenalty, setGapOpenPenalty] = useState(-3);
  const [gapExtensionPenalty, setGapExtensionPenalty] = useState(-1);

  const [result, setResult] = useState<SequenceAlignmentResponse | null>(
    null,
  );
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  async function handleAlign() {
    setError(null);
    setResult(null);

    if (!firstResidues.trim() || !secondResidues.trim()) {
      setError("Enter residues for both sequences before aligning.");
      return;
    }

    if (scoringMethod === "substitution_matrix" && alphabet !== "protein") {
      setError("BLOSUM62 substitution scoring is only available for proteins.");
      return;
    }

    setLoading(true);

    try {
      const response = await alignmentApi.align({
        first_sequence: {
          name: firstName.trim() || "Sequence 1",
          residues: firstResidues.trim(),
          alphabet,
        },
        second_sequence: {
          name: secondName.trim() || "Sequence 2",
          residues: secondResidues.trim(),
          alphabet,
        },
        alignment_type: alignmentType,
        scoring:
          scoringMethod === "substitution_matrix"
            ? {
                method: "substitution_matrix",
                matrix_name: "BLOSUM62",
              }
            : {
                method: "simple",
                match_score: matchScore,
                mismatch_score: mismatchScore,
              },
        gap:
          gapModel === "linear"
            ? {
                model: "linear",
                gap_penalty: gapPenalty,
              }
            : {
                model: "affine",
                gap_open_penalty: gapOpenPenalty,
                gap_extension_penalty: gapExtensionPenalty,
              },
      });

      setResult(response);
    } catch (caught) {
      setError(
        caught instanceof Error
          ? caught.message
          : "An unexpected error occurred while aligning the sequences.",
      );
    } finally {
      setLoading(false);
    }
  }

  function handleReset() {
    setFirstResidues("");
    setSecondResidues("");
    setResult(null);
    setError(null);
  }

  return (
    <section className="alignment-workspace">
      <header className="alignment-header">
        <div>
          <p className="alignment-eyebrow">SEQUENCE ANALYSIS</p>
          <h1>Pairwise Sequence Alignment</h1>
          <p className="alignment-description">
            Compare two biological sequences using global or local alignment.
          </p>
        </div>
      </header>

      <div className="alignment-panel">
        <div className="alignment-panel-heading">
          <div>
            <h2>Input sequences</h2>
            <p>Provide the two sequences you want to compare.</p>
          </div>
        </div>

        <div className="alignment-sequence-grid">
          <div className="alignment-field">
            <label htmlFor="first-sequence-name">First sequence name</label>
            <input
              id="first-sequence-name"
              value={firstName}
              onChange={(event) => setFirstName(event.target.value)}
            />
            <label htmlFor="first-sequence">Residues</label>
            <textarea
              id="first-sequence"
              value={firstResidues}
              onChange={(event) => setFirstResidues(event.target.value)}
              placeholder="Enter DNA, RNA, or protein residues..."
              rows={7}
              spellCheck={false}
            />
          </div>

          <div className="alignment-field">
            <label htmlFor="second-sequence-name">Second sequence name</label>
            <input
              id="second-sequence-name"
              value={secondName}
              onChange={(event) => setSecondName(event.target.value)}
            />
            <label htmlFor="second-sequence">Residues</label>
            <textarea
              id="second-sequence"
              value={secondResidues}
              onChange={(event) => setSecondResidues(event.target.value)}
              placeholder="Enter DNA, RNA, or protein residues..."
              rows={7}
              spellCheck={false}
            />
          </div>
        </div>
      </div>

      <div className="alignment-panel">
        <div className="alignment-panel-heading">
          <div>
            <h2>Alignment configuration</h2>
            <p>Choose the biological alphabet and scoring parameters.</p>
          </div>
        </div>

        <div className="alignment-config-grid">
          <div className="alignment-field">
            <label htmlFor="sequence-alphabet">Sequence alphabet</label>
            <select
              id="sequence-alphabet"
              value={alphabet}
              onChange={(event) =>
                setAlphabet(event.target.value as SequenceAlphabet)
              }
            >
              <option value="dna">DNA</option>
              <option value="rna">RNA</option>
              <option value="protein">Protein</option>
            </select>
          </div>

          <div className="alignment-field">
            <label htmlFor="alignment-type">Alignment type</label>
            <select
              id="alignment-type"
              value={alignmentType}
              onChange={(event) =>
                setAlignmentType(event.target.value as AlignmentType)
              }
            >
              <option value="global">Global (Needleman–Wunsch)</option>
              <option value="local">Local (Smith–Waterman)</option>
            </select>
          </div>

          <div className="alignment-field">
            <label htmlFor="scoring-method">Scoring method</label>
            <select
              id="scoring-method"
              value={scoringMethod}
              onChange={(event) =>
                setScoringMethod(
                  event.target.value as AlignmentScoringMethod,
                )
              }
            >
              <option value="simple">Simple match / mismatch</option>
              <option value="substitution_matrix" disabled={alphabet !== "protein"}>
                BLOSUM62 substitution matrix
              </option>
            </select>
          </div>

          {scoringMethod === "simple" && (
            <>
              <div className="alignment-field">
                <label htmlFor="match-score">Match score</label>
                <input
                  id="match-score"
                  type="number"
                  value={matchScore}
                  onChange={(event) => setMatchScore(Number(event.target.value))}
                />
              </div>

              <div className="alignment-field">
                <label htmlFor="mismatch-score">Mismatch score</label>
                <input
                  id="mismatch-score"
                  type="number"
                  value={mismatchScore}
                  onChange={(event) =>
                    setMismatchScore(Number(event.target.value))
                  }
                />
              </div>
            </>
          )}

          <div className="alignment-field">
            <label htmlFor="gap-model">Gap model</label>
            <select
              id="gap-model"
              value={gapModel}
              onChange={(event) =>
                setGapModel(event.target.value as AlignmentGapModel)
              }
            >
              <option value="linear">Linear</option>
              <option value="affine">Affine</option>
            </select>
          </div>

          {gapModel === "linear" ? (
            <div className="alignment-field">
              <label htmlFor="gap-penalty">Gap penalty</label>
              <input
                id="gap-penalty"
                type="number"
                value={gapPenalty}
                onChange={(event) => setGapPenalty(Number(event.target.value))}
              />
            </div>
          ) : (
            <>
              <div className="alignment-field">
                <label htmlFor="gap-open">Gap opening penalty</label>
                <input
                  id="gap-open"
                  type="number"
                  value={gapOpenPenalty}
                  onChange={(event) =>
                    setGapOpenPenalty(Number(event.target.value))
                  }
                />
              </div>

              <div className="alignment-field">
                <label htmlFor="gap-extension">Gap extension penalty</label>
                <input
                  id="gap-extension"
                  type="number"
                  value={gapExtensionPenalty}
                  onChange={(event) =>
                    setGapExtensionPenalty(Number(event.target.value))
                  }
                />
              </div>
            </>
          )}
        </div>

        {scoringMethod === "substitution_matrix" && (
          <p className="alignment-hint">
            BLOSUM62 is selected for protein sequence scoring.
          </p>
        )}
      </div>

      <div className="alignment-actions">
        <button
          type="button"
          className="alignment-primary-button"
          onClick={handleAlign}
          disabled={loading}
        >
          {loading ? "Aligning sequences..." : "Run alignment"}
        </button>

        <button
          type="button"
          className="alignment-secondary-button"
          onClick={handleReset}
          disabled={loading}
        >
          Reset
        </button>
      </div>

      {error && (
        <div className="alignment-error" role="alert">
          {error}
        </div>
      )}

      {result && (
        <section className="alignment-panel alignment-results">
          <div className="alignment-panel-heading">
            <div>
              <p className="alignment-eyebrow">COMPUTATION COMPLETE</p>
              <h2>Alignment results</h2>
              <p>
                {result.alignment_type === "global" ? "Global" : "Local"}{" "}
                alignment · {result.sequence_count} sequences
              </p>
            </div>
            <div className="alignment-score">
              <span>Alignment score</span>
              <strong>{result.score.score}</strong>
            </div>
          </div>

          <div className="alignment-stat-grid">
            <div className="alignment-stat">
              <span>Alignment length</span>
              <strong>{result.alignment_length}</strong>
            </div>
            <div className="alignment-stat">
              <span>Identity</span>
              <strong>{result.identity_percentage.toFixed(2)}%</strong>
            </div>
            <div className="alignment-stat">
              <span>Similar positions</span>
              <strong>
                {result.similarity_percentage === null
                  ? "N/A"
                  : `${result.similarity_percentage.toFixed(2)}%`}
              </strong>
            </div>
            <div className="alignment-stat">
              <span>Gap count</span>
              <strong>{result.gap_count}</strong>
            </div>
            <div className="alignment-stat">
              <span>Gap percentage</span>
              <strong>{result.gap_percentage.toFixed(2)}%</strong>
            </div>
            <div className="alignment-stat">
              <span>Identical positions</span>
              <strong>{result.identical_positions}</strong>
            </div>
          </div>

          <div className="alignment-output">
            <h3>Aligned sequences</h3>
            {result.aligned_sequences.map((sequence) => (
              <div
                className="alignment-output-row"
                key={sequence.sequence_identity}
              >
                <div className="alignment-output-name">
                  {sequence.sequence_name}
                </div>
                <pre>{sequence.residues}</pre>
              </div>
            ))}
          </div>

          <div className="alignment-score-details">
            <h3>Scoring details</h3>
            <p>
              Scheme: <strong>{result.score.scoring_scheme}</strong>
            </p>
            <p>
              Gap opening penalty:{" "}
              <strong>{result.score.gap_open_penalty}</strong>
            </p>
            <p>
              Gap extension penalty:{" "}
              <strong>{result.score.gap_extension_penalty}</strong>
            </p>
            {result.score.substitution_matrix && (
              <p>
                Substitution matrix:{" "}
                <strong>{result.score.substitution_matrix}</strong>
              </p>
            )}
          </div>
        </section>
      )}
    </section>
  );
}
