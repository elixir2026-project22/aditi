# Aditi — Biological Pathway and Sequence Analysis Platform

**Project Status:** Prototype — Core implementation and verification completed
**Technology Stack:** Python, FastAPI, React, TypeScript, Vite
**Project:** Aditi

---

## 1. Project Overview

Aditi is a modular biological pathway and sequence analysis platform designed to support the ingestion, normalization, analysis, and visualization of biological data.

The platform currently focuses on two major areas:

1. **Biological Pathway Visualization** — importing SBML biological models, converting their contents into an internal domain representation, constructing pathway graphs, and generating visual scenes.
2. **Pairwise Sequence Alignment** — performing global and local sequence alignment for DNA, RNA, and protein sequences using established alignment algorithms and configurable scoring schemes.

The objective is to establish a modular and extensible foundation for future computational biology capabilities.

## 2. System Architecture

Aditi follows a layered architecture that separates biological domain concepts from data ingestion, computational algorithms, visualization, and API interfaces.

The principal architectural layers are:

| Layer | Responsibility |
|---|---|
| Domain | Biological entities, sequences, pathways, reactions, graphs, and alignment models |
| Data | Parsing, importing, and normalizing external biological data |
| Modules | Computational algorithms and biological analysis workflows |
| Visualization | Transformation of biological models and results into visualization scenes |
| Application | Lifecycle management, orchestration, and application services |
| API | HTTP endpoints, request validation, and response serialization |
| Frontend | User interface and interaction with backend services |

This separation supports independent testing, maintainability, and future expansion.

## 3. Implemented Features

### 3.1 Biological Pathway Visualization

The pathway module supports:

- SBML document ingestion.
- XML parsing and biological model extraction.
- Metabolite and reaction normalization.
- Reactant and product relationships.
- Modifier species references.
- Reaction stoichiometric coefficients.
- Reversible reaction information.
- Biological pathway graph construction.
- Hierarchical and force-directed layout support.
- Visualization scene generation.
- Frontend pathway exploration and graph rendering.

The graph representation distinguishes three reaction edge roles:

- Reactant
- Product
- Modifier

This distinction allows regulatory relationships to be represented separately from ordinary reaction inputs and outputs.

### 3.2 SBML Import Pipeline

The implemented import pipeline follows this sequence:

**SBML XML → Parser → Normalization → Domain Model → Pathway Graph → Layout → Visualization Scene → API Response → Frontend**

The importer has been tested against real biological models obtained from BioModels.

#### Real-world model verification

| Model | BioModels ID | Result |
|---|---|---|
| Hynne2001 — Glycolysis | BIOMD0000000061 | Successfully imported and visualized |
| Sass2009 — α-synuclein Parkinson's disease model | BIOMD0000000575 | Successfully imported and visualized |

For the second model, the complete backend visualization workflow produced:

| Metric | Result |
|---|---:|
| Graph nodes | 134 |
| Graph edges | 332 |
| Modifier edges | 132 |
| Reactions | 58 |

The second model was also successfully imported through the HTTP API and rendered in the frontend.

### 3.3 Pairwise Sequence Alignment

The sequence analysis module supports biological sequences with three alphabets:

- DNA
- RNA
- Protein

Implemented alignment algorithms:

| Algorithm | Alignment type |
|---|---|
| Needleman–Wunsch | Global |
| Smith–Waterman | Local |

Implemented scoring capabilities:

- Simple match and mismatch scoring.
- Configurable linear gap penalties.
- Affine gap penalties.
- BLOSUM62 substitution matrix for protein alignment.

Alignment results include:

- Aligned sequences.
- Alignment score.
- Alignment length.
- Identical positions.
- Sequence identity percentage.
- Gap count and gap percentage.
- Position mappings.
- Scoring configuration details.

The API exposes pairwise alignment through:

`POST /api/v1/alignments/pairwise`

Multiple sequence alignment is not currently implemented.

## 4. DNA Alignment Verification

DNA alignment was manually verified through the actual Aditi frontend and backend.

The following scenarios were tested:

| Test | Expected behaviour | Result |
|---|---|---|
| Short DNA global alignment | Correct matching and gap placement | Passed |
| Longer DNA alignment | Correct alignment of longer sequences | Passed |
| DNA local alignment | Identify shared subsequence | Passed |
| Smith–Waterman | Return the best local matching region | Passed |
| Affine gap penalties | Apply gap-opening and extension penalties | Passed |
| Invalid DNA residue | Reject invalid nucleotide characters | Passed |
| DNA/RNA alphabet mismatch | Reject incompatible sequence alphabets | Passed |
| BLOSUM62 with DNA | Reject unsupported scoring configuration | Passed |

### Representative alignment results

**Global alignment**

Sequences: `ACGT` and `AGT`

- Alignment score: 4
- Alignment length: 4
- Identity: 75%
- Gap count: 1

**Longer DNA alignment**

- Alignment score: 172
- Alignment length: 100
- Identity: 93%
- Gap count: 7

**Local DNA alignment**

- Alignment score: 50
- Alignment length: 25
- Identity: 100%
- Gap count: 0

**Affine gap alignment**

- Alignment score: 16
- Alignment length: 12
- Identity: 83.33%
- Gap count: 2

These results demonstrate that the implemented DNA alignment workflows operate through the integrated application.

## 5. Backend API and Frontend Integration

The backend uses Python and FastAPI to expose biological processing capabilities.

Implemented endpoints include:

- Health and application status.
- SBML pathway import and visualization.
- Pairwise sequence alignment.

The frontend uses React, TypeScript, and Vite.

Implemented frontend workspaces include:

**Pathway Maps**
- SBML file import.
- Biological pathway graph visualization.
- Graph exploration.
- Node properties.
- Full-screen visualization.

**Sequence Alignment**
- Sequence input and alphabet selection.
- Global and local alignment configuration.
- Scoring and gap configuration.
- Alignment computation.
- Alignment result visualization.

**Protein Structure**
- Reserved workspace.
- Advanced structure visualization is not yet implemented.

## 6. Testing and Verification

Testing has been performed at multiple levels.

### Backend testing

- Unit tests for domain models and biological data processing.
- SBML parser tests.
- SBML normalization and conversion tests.
- Modifier relationship and graph construction tests.
- Alignment algorithm tests.
- Alignment API integration tests.

The dedicated pairwise alignment API integration suite completed with:

**10 passed.**

The SBML parser, converter, graph construction, and visualization workflow were also verified against the two real BioModels examples.

### Frontend testing

- Production build completed successfully using Vite.
- Pathway Maps workspace tested with real SBML models.
- Sequence Alignment workspace tested with DNA global and local alignments.
- Linear and affine gap configurations tested.
- Invalid DNA input and incompatible scoring configurations tested.

## 7. Current Limitations

Aditi is an evolving prototype. The following limitations are acknowledged.

### SBML compatibility

The current SBML importer supports the biological network structures required by the tested models, but it does not yet implement the complete SBML specification.

Features requiring further support include:

- Full kinetic law and MathML interpretation.
- Compartment semantics.
- SBML rules and events.
- Constraints.
- Complete annotation and extension-package handling.
- Additional SBML Level and Version variations.

Some BioModels documents may therefore fail to import because they use constructs that are not yet supported.

The current pathway visualization workflow represents biological network topology; it does not simulate the underlying biochemical dynamics.

### Sequence analysis

- Multiple sequence alignment is not implemented.
- Advanced biological sequence analysis workflows remain future work.
- Additional substitution matrices and scoring strategies may be added later.

### Protein structure

Protein structure processing and 3D visualization remain unimplemented.

## 8. Future Development

Potential future improvements include:

1. Broader SBML Level and Version compatibility.
2. Improved handling of kinetic laws and MathML.
3. Expanded biological model support.
4. Multiple sequence alignment.
5. Additional sequence analysis algorithms.
6. Protein structure ingestion and 3D visualization.
7. More advanced biological data exploration and analysis.

These are future development directions, not features claimed as complete in the current implementation.

## 9. Conclusion

Aditi has established a working foundation for biological pathway visualization and pairwise sequence alignment.

The platform successfully imports and visualizes two real BioModels examples, constructs pathway graphs with reactant, product, and modifier relationships, and provides integrated global and local sequence alignment for DNA, RNA, and protein alphabets.

The implementation is supported by a modular architecture, backend tests, API integration tests, and frontend verification.

The current prototype provides a foundation for expanding Aditi into a broader biological data analysis and visualization platform.

---

**Project:** Aditi
**Status:** Core prototype implemented and verified
**Report Scope:** Current implemented functionality and observed test results
