# Aditi: A Modular Platform for Biological Pathway Visualization and Sequence Analysis

**Project:** Aditi  
**Repository:** https://github.com/elixir2026-project22/aditi  
**Primary technology stack:** Python, FastAPI, React, TypeScript, Vite  
**Software license:** MIT  
**Project context:** BioHackathon Europe 2026 — Open Pathway Maps (Project 22), with a planned extension toward synchronized sequence and structural visualization (Project 9).

---

## 1. Abstract

Biological systems are commonly studied through different computational tools for sequence analysis, metabolic pathway representation, molecular interaction networks, and protein structure visualization. Although these tools provide valuable individual capabilities, moving between them often requires separate data models, incompatible representations, and disconnected workflows.

Aditi is an evolving modular platform intended to provide a unified foundation for biological data processing and visualization. Its initial development focuses on biological pathway visualization, particularly the ingestion and processing of Systems Biology Markup Language (SBML) models, conversion into normalized biological entities and reaction networks, graph construction, and interactive visualization. The platform also introduces a biological sequence analysis foundation, including sequence representation, FASTA ingestion, and global and local pairwise alignment.

The implementation currently includes a Python-based backend, a FastAPI application interface, and a React-based frontend. The pathway workflow has been validated against real models obtained from BioModels, while the sequence alignment implementation has been tested with DNA, RNA, and protein-related functionality, including substitution-matrix scoring and affine gap penalties.

Aditi is being developed in the context of BioHackathon Europe 2026 Project 22, Open Pathway Maps. Its longer-term direction also considers Project 9, From Alignment to Insight: Synchronized MSA and 3D Structure Visualization. The present implementation establishes foundations for this integration, but multiple sequence alignment, protein structure rendering, and synchronized structure-analysis workflows remain future development objectives.

This report documents the current architecture, implemented functionality, processing pipelines, validation, limitations, and planned development.

## 2. Motivation and Background

Biological research increasingly depends on the ability to interpret relationships between different types of biological information.

A metabolic pathway model describes reactions, metabolites, and their relationships. A biological sequence provides information about the composition and organization of DNA, RNA, or protein molecules. A protein structure provides a spatial representation of molecular organization.

These representations are related, but they are frequently handled by separate software systems.

Several practical challenges arise:

- Biological models originate from different data formats and repositories.
- Structured biological data must be normalized before it can be visualized consistently.
- Large reaction networks require suitable graph representations and layout algorithms.
- Sequence analysis and pathway analysis often exist in separate workflows.
- Moving between biological representations can require manual data transfer.
- Different visualization tools may maintain independent models of the same biological entities.

Aditi is intended to address these challenges by establishing a modular application architecture in which biological data can be ingested, normalized, represented through domain models, processed by specialized workflows, and presented through a unified interface.

The initial implementation prioritizes pathway visualization and pairwise sequence analysis. More advanced biological integrations are planned incrementally.

## 3. Project Objectives

The current development has the following objectives:

1. Establish a modular foundation for biological data processing.
2. Implement domain representations for biological entities and pathways.
3. Support ingestion and processing of SBML pathway models.
4. Convert biological reactions into a graph representation.
5. Provide hierarchical and force-directed graph layouts.
6. Visualize pathway networks interactively.
7. Establish biological sequence representations for DNA, RNA, and proteins.
8. Implement global and local pairwise sequence alignment.
9. Expose backend functionality through a structured API.
10. Provide a unified frontend for pathway and sequence-analysis workflows.

Longer-term objectives include multiple sequence alignment, protein structure visualization, synchronized sequence-to-structure exploration, and integration with additional biological data resources.

## 4. System Architecture

Aditi follows a modular architecture that separates application infrastructure, biological domain models, data ingestion, processing workflows, API services, and frontend presentation.

The principal implementation areas are:

- Application lifecycle and infrastructure.
- Biological domain models.
- Data parsers and normalization.
- Pathway processing and graph construction.
- Sequence processing and alignment.
- Application services and API endpoints.
- Frontend workspaces and visualization components.

The architecture is designed to keep biological domain logic independent of individual presentation components wherever practical.

### 4.1 Backend

The backend is implemented in Python.

It contains the core application infrastructure, biological domain models, data-processing components, and application services.

FastAPI provides the HTTP interface through which the frontend communicates with backend functionality.

The backend is responsible for:

- Receiving and validating requests.
- Parsing biological input data.
- Constructing domain objects.
- Running pathway and alignment workflows.
- Returning structured results.
- Handling invalid inputs and workflow errors.

### 4.2 Frontend

The frontend uses React, TypeScript, and Vite.

It provides the user-facing application and currently includes:

- Pathway Maps workspace.
- Sequence Alignment workspace.
- Protein Structure workspace placeholder.

The frontend communicates with backend APIs rather than independently implementing the biological processing algorithms.

### 4.3 Application infrastructure

The application foundation includes components for:

- Application lifecycle management.
- Events and event handling.
- Resources.
- Commands.
- Cancellation.
- Error handling and logging.

These components establish a common infrastructure for the current workflows and future extensions.

The current implementation is a modular application with event-oriented infrastructure. It should not be interpreted as a fully distributed actor system.

## 5. Biological Domain Foundation

Aditi uses domain models to represent biological information independently of the raw input format.

The current domain foundation includes biological entity identity and pathway-related representations.

### 5.1 Biological entities and identity

Biological entities are represented through domain-level models rather than being treated only as parser output.

An identity foundation supports consistent references to biological entities across processing stages.

This provides a basis for normalization and for future connections between different biological representations.

### 5.2 Pathway domain

The pathway domain includes representations for:

- Metabolites.
- Reactions.
- Pathways.
- Graph nodes and edges.
- Entity identities.

A pathway is therefore represented as a structured biological model rather than merely a collection of visualization elements.

This separation allows the same pathway representation to be processed by different layout and visualization workflows.

## 6. SBML Ingestion and Pathway Processing

A major component of the current implementation is the SBML processing workflow.

SBML is a standardized format used to represent computational models of biological processes, including biochemical reactions and their associated species.

Aditi uses SBML as an input format for constructing biological pathway representations.

### 6.1 Processing pipeline

The implemented pathway workflow follows these stages:

1. SBML input is received.
2. The parser reads the XML document.
3. Species and reaction information are extracted.
4. Reactant, product, and modifier references are collected.
5. Parsed information is passed to the normalization layer.
6. Domain-level metabolites, reactions, and pathways are constructed.
7. The pathway graph is generated.
8. A selected layout algorithm calculates graph positions.
9. The resulting visualization data is returned to the frontend.
10. The frontend renders the interactive pathway network.

The processing pipeline separates raw document parsing from biological normalization and graph visualization.

### 6.2 SBML parser

The SBML parser currently extracts:

- Species.
- Reactions.
- Reactant references.
- Product references.
- Modifier references.

It also performs validation of relevant references and stoichiometric values.

The current parser uses Python's standard XML processing facilities and deliberately rejects unsafe document constructs such as DOCTYPE and ENTITY declarations.

The implementation validates that referenced species exist and that stoichiometric values are positive and finite.

The parser is not yet a complete implementation of the entire SBML specification.

### 6.3 Normalization

Parsed SBML data is transformed into domain-level biological representations.

The normalization stage is responsible for translating source-level species and reaction information into the internal pathway model.

This separation is important because the visualization system should not depend directly on the internal XML structure of an input document.

The normalization stage also handles the relationship between modifier references in the source model and the internal reaction representation.

### 6.4 Graph construction

After normalization, the pathway is represented as a graph.

The graph contains biological entities and their relationships.

The current graph representation supports:

- Metabolite nodes.
- Reaction nodes.
- Reactant relationships.
- Product relationships.
- Modifier relationships.

This representation allows pathway information to be visualized and explored through graph algorithms.

### 6.5 Layout algorithms

Two layout approaches are currently implemented:

**Hierarchical layout**

The hierarchical layout uses strongly connected component analysis and topological organization to arrange graph elements in layers.

This provides a structured representation of reaction networks and their relationships.

**Force-directed layout**

The force-directed layout provides an alternative spatial arrangement based on graph relationships.

It is useful when a more organic network representation is preferable to a layered arrangement.

The frontend can display pathway data using the available layout options.

### 6.6 Interactive pathway visualization

The Pathway Maps workspace currently supports:

- SBML model import.
- Interactive graph visualization using Cytoscape.
- Pathway exploration.
- Properties panels.
- Graph inspection.
- Fullscreen visualization.

The objective is to allow users to move from a biological model to an interactive representation without manually reconstructing its reaction network.

## 7. Real Biological Model Validation

The pathway workflow has been tested with real models obtained from BioModels.

This is important because validation against actual curated models provides stronger evidence than testing only with manually constructed examples.

### 7.1 Hynne2001 glycolysis model

The model BIOMD0000000061, associated with Hynne2001 glycolysis, was imported and rendered through the Aditi pathway workflow.

This provided an initial validation of the SBML ingestion and pathway visualization pipeline.

### 7.2 Alpha-synuclein model

The model BIOMD0000000575, associated with the Sass2009 alpha-synuclein Parkinson's disease model, was also used for validation.

The parser preserved nine modifier references for the relevant reaction during source-level extraction.

The normalization stage handled these references when constructing the internal reaction representation.

The resulting graph contained:

- 134 nodes.
- 332 edges.
- 58 reaction nodes.
- 132 modifier edges.

The SBML visualization workflow completed successfully, and the model was returned through the API with HTTP 200 during endpoint testing.

The model was also successfully rendered in the frontend.

These results demonstrate that the current pathway workflow can process and visualize real biological models beyond the simplest manually created examples.

They do not establish complete SBML compatibility or universal support for all BioModels records.

## 8. Biological Sequence Foundation

In addition to pathway visualization, Aditi includes a biological sequence-processing foundation.

This is an important step toward connecting sequence-level information with pathway and structural representations.

### 8.1 Sequence alphabets

The sequence domain supports:

- DNA.
- RNA.
- Protein.

The alphabet representation provides a basis for validating sequence symbols and distinguishing different biological sequence types.

### 8.2 Biological sequence model

The BiologicalSequence domain model represents a biological sequence with its associated alphabet and sequence information.

This provides a common representation for sequence-processing workflows.

### 8.3 FASTA ingestion

The current implementation includes FASTA parsing and sequence import functionality.

FASTA is used as a common input format for biological sequence data.

The parser provides a structured representation that can be passed into the sequence-analysis domain.

## 9. Pairwise Sequence Alignment

Aditi currently implements global and local pairwise sequence alignment.

These algorithms establish the initial computational foundation for sequence comparison.

### 9.1 Alignment domain

The alignment domain includes representations for:

- Aligned sequences.
- Alignment scores.
- Alignment types.
- Alignment results.

This separates the representation of an alignment from the algorithms that calculate it.

### 9.2 Global alignment

Global alignment is implemented using the Needleman-Wunsch algorithm.

It attempts to align two sequences across their full lengths.

This is useful when comparing sequences expected to share broad overall similarity.

### 9.3 Local alignment

Local alignment is implemented using the Smith-Waterman algorithm.

It identifies high-scoring local regions between two sequences.

This is useful when only a portion of two sequences is expected to be similar.

### 9.4 Scoring systems

The alignment implementation supports:

- Simple match and mismatch scoring.
- Substitution-matrix scoring.
- BLOSUM62.
- Linear gap penalties.
- Affine gap penalties.

BLOSUM62 is restricted to protein alignment rather than being applied to DNA or RNA sequences.

### 9.5 Alignment service

The AlignmentService provides a common entry point for selecting and executing supported pairwise alignment workflows.

Global and local alignment are currently supported.

Multiple sequence alignment is not yet implemented. Requests for unsupported multiple alignment are rejected rather than being treated as completed functionality.

### 9.6 Alignment API

The backend exposes pairwise alignment through:

`POST /api/v1/alignments/pairwise`

The endpoint accepts alignment input and returns structured alignment results.

Invalid sequence types, incompatible alphabets, unsupported scoring combinations, and other invalid requests are handled through validation and appropriate API error responses.

The API route maps relevant ValueError and KeyError conditions to HTTP 422 responses.

The application factory also supports dependency injection for the alignment API service, making the API easier to test independently.

## 10. Frontend Sequence Alignment Workspace

The Sequence Alignment workspace provides an interface for the currently implemented pairwise alignment functionality.

Its capabilities include:

- Sequence input.
- DNA, RNA, and protein selection.
- Global and local alignment selection.
- Simple scoring.
- BLOSUM62 selection for protein sequences.
- Match and mismatch scoring.
- Linear and affine gap penalties.
- Alignment submission.
- Reset functionality.
- Loading and error states.
- Alignment result display.
- Alignment metrics.
- Aligned sequence rows.

The interface communicates with the backend API and displays the resulting alignment.

The frontend does not replace the backend algorithms; it acts as the interactive presentation layer for the sequence-analysis workflow.

## 11. API and Application Integration

FastAPI provides the interface between the frontend and backend application services.

The API layer exposes functionality through structured endpoints and keeps request handling separate from the underlying biological domain logic.

Current API capabilities include:

- Health checks.
- Pathway-related operations.
- SBML import.
- Layout-related operations.
- Pairwise sequence alignment.

The pathway and sequence workflows share the same application foundation while retaining their own specialized domain models and services.

## 12. Testing and Validation

Testing has been performed across backend domain logic, parsing, API functionality, frontend integration, and real biological model processing.

### 12.1 Pathway processing

The pathway workflow has been tested using:

- Parser-level tests.
- Normalization tests.
- Domain-model tests.
- Graph construction tests.
- Layout tests.
- SBML import workflow tests.
- Real BioModels examples.

The alpha-synuclein model provided a more complex validation case involving modifier relationships and a larger reaction network.

### 12.2 Sequence processing

The sequence and alignment implementation has been tested for:

- DNA global alignment.
- Protein and substitution-matrix scoring support.
- Local alignment.
- Linear gap penalties.
- Affine gap penalties.
- Invalid residue rejection.
- Incompatible DNA/RNA sequence rejection.
- Rejection of BLOSUM62 for DNA.

Representative manual validation results include:

| Test case | Observed result |
|---|---|
| DNA global alignment: ACGT vs AGT | Score 4, 75% identity, one gap |
| Longer DNA global alignment | Score 172, alignment length 100, 93% identity, 7 gaps |
| Smith-Waterman local alignment | Score 50, alignment length 25, 100% identity |
| Affine gap alignment | Score 16, alignment length 12, 83.33% identity |
| Invalid DNA residue | Rejected |
| DNA/RNA alphabet mismatch | Rejected |
| BLOSUM62 applied to DNA | Rejected |

These are representative validation cases, not a formal performance benchmark.

### 12.3 API tests

The pairwise alignment API test suite completed successfully with 10 passing tests.

The frontend production build also completed successfully using the Vite build process.

A non-blocking large-chunk warning was observed during the frontend build and remains an optimization opportunity.

### 12.4 Manual integration validation

The user interface was manually tested with pathway import and sequence alignment workflows.

The real BioModels examples were successfully processed through the backend and rendered in the frontend.

## 13. Current Implementation Status

The following table distinguishes implemented functionality from future work.

| Component | Status |
|---|---|
| Modular application foundation | Implemented |
| Application lifecycle and infrastructure | Implemented |
| Biological entity identity | Implemented |
| Pathway domain models | Implemented |
| SBML parser and normalization | Implemented within current supported scope |
| Reaction graph construction | Implemented |
| Hierarchical layout | Implemented |
| Force-directed layout | Implemented |
| Interactive pathway visualization | Implemented |
| Real BioModels import validation | Demonstrated |
| DNA/RNA/protein sequence foundation | Implemented |
| FASTA ingestion | Implemented |
| Global pairwise alignment | Implemented |
| Local pairwise alignment | Implemented |
| BLOSUM62 scoring | Implemented |
| Affine gap scoring | Implemented |
| Pairwise alignment API | Implemented |
| Sequence Alignment workspace | Implemented |
| Multiple sequence alignment | Planned |
| Protein structure parsing and 3D rendering | Planned |
| Alignment-to-structure mapping | Planned |
| Synchronized MSA and 3D visualization | Planned |
| SBGN integration | Planned |
| UNICON integration | Planned |
| External biological resource adapters | Planned |
| AI-assisted biological analysis | Future research direction |

## 14. Current Limitations

Aditi is an evolving prototype. Its present functionality should be interpreted within the scope of the implemented components.

### 14.1 SBML coverage

The current SBML parser supports a subset of the SBML document structure.

It does not yet provide complete coverage of all SBML levels, versions, packages, or advanced model constructs.

Features such as comprehensive kinetic-law processing and the full Flux Balance Constraints (FBC) package are not currently implemented.

### 14.2 Pathway visualization

The current graph visualization provides interactive pathway exploration, but additional work is required for larger networks, richer biological notation, and more advanced graph interaction.

Formal comparative benchmarking of layout algorithms has not yet been completed.

### 14.3 Sequence analysis

The current sequence-analysis functionality is limited to pairwise alignment.

Multiple sequence alignment, profile-based analysis, and other advanced sequence-analysis workflows remain future work.

### 14.4 Protein structures

The Protein Structure workspace is currently a placeholder.

Protein structure parsing, 3D rendering, residue-level mapping, and synchronized structural analysis have not yet been implemented.

### 14.5 External integrations

Integration with external biological resources and visualization systems remains a planned development area.

Potential future integrations include Reactome, BRENDA, Metabolic Atlas, SBGN-compatible workflows, and UNICON-related capabilities.

### 14.6 AI-assisted analysis

AI-assisted interpretation, automated biological insights, and predictive analysis are not part of the current verified implementation.

They may be explored after the underlying biological data representations and processing workflows have matured.

## 15. Future Development Roadmap

The future development of Aditi is organized around incremental improvements to the existing architecture.

### Phase 1: Strengthen existing workflows

- Expand SBML parser coverage.
- Improve validation and error reporting.
- Improve pathway visualization for larger networks.
- Refine frontend usability.
- Add more real biological model validation cases.
- Improve automated integration testing.

### Phase 2: Extend pathway interoperability

- Investigate SBGN-compatible pathway representation.
- Explore UNICON integration.
- Add adapters for external biological databases.
- Improve support for exchanging normalized biological models.

### Phase 3: Advance sequence analysis

- Implement multiple sequence alignment.
- Add alignment visualization improvements.
- Support larger sequence collections.
- Introduce additional alignment algorithms and scoring strategies where appropriate.

### Phase 4: Introduce structural biology

- Add protein structure file ingestion.
- Introduce a protein structure domain model.
- Implement 3D structure visualization.
- Establish residue and sequence correspondence.
- Connect sequence alignment results with structural representations.

### Phase 5: Unified biological exploration

- Develop synchronized sequence, pathway, and structure workspaces.
- Connect biological entities across different representations.
- Explore cross-domain navigation and contextual analysis.
- Investigate AI-assisted biological interpretation.

These phases are a proposed roadmap and do not imply that the corresponding functionality is already available.

## 16. Relationship to BioHackathon Europe 2026

Aditi originated primarily in the context of BioHackathon Europe 2026 Project 22: Open Pathway Maps.

The initial development direction focuses on pathway-model ingestion, normalization, graph construction, and interactive visualization.

The project also considers Project 9: From Alignment to Insight: Synchronized MSA and 3D Structure Visualization, as a complementary extension.

The current pairwise alignment foundation is a starting point for that direction. It is not equivalent to the full Project 9 objective, which requires multiple sequence alignment, structural representation, and synchronized exploration.

The long-term intention is to develop a shared biological visualization platform where pathway, sequence, and structural representations can coexist within a consistent application architecture.

## 17. Software Availability

The Aditi source code is available at:

https://github.com/elixir2026-project22/aditi

The repository contains the backend, frontend, implementation, tests, and project documentation.

The software is distributed under the MIT License.

The repository is intended to support transparent development, reproducibility, collaboration, and future contributions.

## 18. Conclusion

Aditi has progressed from an initial biological visualization concept into a working modular prototype with two principal areas of functionality: pathway visualization and pairwise sequence analysis.

The pathway workflow supports SBML ingestion, biological normalization, reaction graph construction, layout generation, and interactive visualization. Its processing pipeline has been validated against real BioModels examples, including the Hynne2001 glycolysis and Sass2009 alpha-synuclein models.

The sequence-analysis foundation supports DNA, RNA, and protein sequence representations, FASTA ingestion, global and local pairwise alignment, BLOSUM62 scoring, and linear and affine gap penalties.

Together, these capabilities establish a foundation for a broader biological visualization environment.

The next stage is to improve the maturity and interoperability of the current workflows while developing the planned multiple sequence alignment and protein structure capabilities associated with the longer-term Project 9 direction.

Aditi is therefore best understood as an evolving modular platform: its current implementation provides functional pathway and sequence-analysis capabilities, while its longer-term objective is to connect different biological representations through a unified and extensible environment.