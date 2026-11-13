# Aditi: BioHackathon Project Progress, Contributions, and Future Integration

**Project:** Aditi  
**Primary project alignment:** BioHackathon Europe 2026 — Project 22: Open Pathway Maps  
**Complementary project alignment:** BioHackathon Europe 2026 — Project 9: From Alignment to Insight: Synchronized MSA and 3D Structure Visualization  
**Repository:** https://github.com/elixir2026-project22/aditi  
**Status:** Working prototype with pathway visualization and pairwise sequence alignment capabilities.

---

## 1. Overview

Aditi is a modular biological visualization and analysis platform developed in the context of BioHackathon Europe 2026.

Its primary foundation is Project 22, Open Pathway Maps, which focuses on making biological pathway information accessible, interoperable, and easier to explore through visualization.

During development, the scope of Aditi expanded beyond pathway visualization. A biological sequence-processing and pairwise alignment foundation was introduced to establish a path toward connecting pathway information with sequence-level and structural biological data.

This creates a natural point of connection with Project 9, From Alignment to Insight: Synchronized MSA and 3D Structure Visualization.

The intention is not to treat these projects as unrelated applications. Instead, Aditi is being developed as a shared modular environment in which capabilities from both project directions can eventually be integrated.

This document describes the motivation, current progress, implementation, project alignment, and future development direction.

## 2. Origin and Motivation

Aditi began with the goal of building a biological visualization environment centered on pathway data.

The initial development focused on the challenges involved in converting biological pathway models into interactive representations.

A pathway model contains biological entities and relationships that must be interpreted, normalized, and organized before they can be explored effectively.

Rather than building a frontend that only displays preformatted diagrams, the project aimed to establish a complete processing workflow:

- Import biological model data.
- Extract biological entities and relationships.
- Normalize the data into internal domain representations.
- Construct a graph.
- Apply suitable layout algorithms.
- Present the resulting network interactively.

As the architecture developed, it became clear that the same platform could provide a foundation for other biological visualization workflows.

Sequence analysis was therefore introduced as a second capability area.

This extension provides a basis for future integration with protein structure visualization and synchronized analysis workflows.

## 3. Relationship with Project 22: Open Pathway Maps

Project 22 is the primary scientific and technical foundation of Aditi.

The work aligns with the goal of processing and visualizing biological pathway information in a reusable and extensible manner.

### 3.1 Contribution to pathway ingestion

Aditi currently supports SBML-based pathway ingestion.

The parser extracts species, reactions, reactants, products, and modifier references from supported SBML documents.

This provides a direct route from a standardized biological model to the platform's internal pathway representation.

### 3.2 Contribution to normalization

The project separates source-level parsing from domain-level representation.

This means that raw XML structures do not need to be passed directly into the graph visualization system.

Instead, biological information is converted into internal representations of metabolites, reactions, pathways, and relationships.

This approach establishes a foundation for adding more input formats and external biological data adapters.

### 3.3 Contribution to graph representation

Aditi converts normalized pathway data into a graph representation.

The graph captures metabolite and reaction relationships, including reactant, product, and modifier connections.

This allows pathway information to be processed using graph algorithms and visualized interactively.

### 3.4 Contribution to layout and visualization

Two layout approaches are currently implemented:

- Hierarchical layout using strongly connected component analysis and topological organization.
- Force-directed layout for an alternative network arrangement.

The frontend uses Cytoscape to display the graph and provides pathway exploration, properties panels, and fullscreen visualization.

### 3.5 Validation using real biological models

The pathway pipeline has been tested using real BioModels examples.

The Hynne2001 glycolysis model, BIOMD0000000061, was successfully imported and rendered.

The Sass2009 alpha-synuclein model, BIOMD0000000575, was also processed successfully.

For the latter model, the resulting graph contained 134 nodes and 332 edges, including 58 reaction nodes and 132 modifier edges.

The model was successfully returned through the API and rendered in the frontend.

These validations demonstrate the current workflow's practical ability to process real biological model data.

They do not establish complete compatibility with every SBML feature or model.

## 4. Relationship with Project 9: From Alignment to Insight

Project 9 focuses on connecting multiple sequence alignment with three-dimensional protein structure visualization and synchronized exploration.

Aditi's current sequence-analysis foundation provides an initial step toward this broader direction.

However, it is important to distinguish the current implementation from the full Project 9 objective.

### 4.1 Current sequence-analysis foundation

Aditi currently includes:

- DNA, RNA, and protein sequence representations.
- FASTA parsing and import.
- Alignment domain models.
- Global pairwise alignment using Needleman-Wunsch.
- Local pairwise alignment using Smith-Waterman.
- Simple match and mismatch scoring.
- BLOSUM62 substitution-matrix scoring.
- Linear and affine gap penalties.
- A pairwise alignment API.
- An interactive Sequence Alignment workspace.

These components provide a functional sequence-analysis foundation.

### 4.2 What remains to be implemented for Project 9

The following capabilities are not yet implemented:

- Multiple sequence alignment.
- MSA visualization.
- Protein structure file parsing.
- Three-dimensional protein structure rendering.
- Residue-level sequence-to-structure mapping.
- Synchronized navigation between aligned sequences and 3D structures.
- Integrated analysis of alignment and structural information.

The current Protein Structure workspace is a placeholder.

The pairwise alignment functionality should therefore be understood as groundwork for the Project 9 direction rather than a completed implementation of Project 9.

### 4.3 Planned integration

The intended development sequence is:

1. Extend the sequence domain and processing infrastructure.
2. Implement multiple sequence alignment.
3. Develop an interactive MSA visualization.
4. Introduce protein structure data models.
5. Implement 3D protein structure visualization.
6. Establish mappings between sequence positions, alignment columns, and structural residues.
7. Introduce synchronized interaction between MSA and structure views.

This would allow a user to explore sequence conservation and structural context within a connected workflow.

For example, selecting an alignment position could eventually highlight the corresponding residue in a protein structure.

This is a planned interaction model, not a current feature.

## 5. A Unified Platform Direction

The central architectural idea behind Aditi is to develop one modular platform rather than separate pathway and sequence-analysis applications.

Pathway models, biological sequences, and protein structures describe different aspects of biological systems.

They can become more useful when users can navigate between them through consistent representations and interactions.

The intended relationship can be summarized as follows:

### Pathway layer — Project 22

- SBML ingestion.
- Biological normalization.
- Metabolite and reaction representation.
- Graph construction.
- Pathway layout.
- Interactive pathway exploration.

### Sequence and structural layer — Project 9

- Sequence ingestion.
- Pairwise alignment foundation.
- Future multiple sequence alignment.
- Future protein structure parsing.
- Future 3D visualization.
- Future synchronized sequence and structure interaction.

### Shared platform layer

Both directions can use common application infrastructure, biological entity identity, data-processing conventions, API services, and frontend integration patterns.

This creates an opportunity for a unified environment in which pathway-level and molecular-level information can eventually be explored together.

The shared platform direction is an architectural goal. The full cross-domain connections have not yet been implemented.

## 6. Current Development Progress

The following sections summarize the work completed so far.

### 6.1 Application foundation

Implemented:

- Modular application structure.
- Application lifecycle management.
- Event infrastructure.
- Resource handling.
- Command infrastructure.
- Cancellation support.
- Error handling and logging.

This provides the foundation for the current biological workflows.

### 6.2 Biological domain foundation

Implemented:

- Biological entity identity.
- Metabolite representation.
- Reaction representation.
- Pathway representation.
- Graph node and relationship models.
- Biological sequence representation.
- Alignment result models.

### 6.3 Pathway processing

Implemented:

- SBML parser.
- Source-level extraction of species and reaction references.
- Validation of relevant species references.
- Stoichiometric validation.
- SBML normalization.
- Domain-level pathway construction.
- Reaction graph generation.
- Modifier relationship representation.
- Hierarchical layout.
- Force-directed layout.
- SBML visualization workflow.

### 6.4 Sequence processing

Implemented:

- DNA alphabet.
- RNA alphabet.
- Protein alphabet.
- Biological sequence model.
- FASTA parser.
- Sequence import service.
- Alignment domain.
- Alignment scoring.
- BLOSUM62.
- Linear gap scoring.
- Affine gap scoring.
- Needleman-Wunsch global alignment.
- Smith-Waterman local alignment.
- Pairwise alignment service.

### 6.5 Backend integration

Implemented:

- FastAPI application.
- Health and pathway-related APIs.
- SBML import API.
- Layout-related API functionality.
- Pairwise alignment API.
- Dependency-injectable alignment API service.
- Structured validation and error responses.

### 6.6 Frontend integration

Implemented:

- React and TypeScript application.
- Pathway Maps workspace.
- Interactive Cytoscape visualization.
- SBML import workflow.
- Pathway explorer and properties panels.
- Fullscreen graph display.
- Sequence Alignment workspace.
- Sequence type selection.
- Alignment mode selection.
- Scoring and gap configuration.
- Alignment result visualization.
- Error and loading states.
- Protein Structure workspace placeholder.

## 7. Validation and Results

Aditi has been validated through automated tests, manual API checks, frontend builds, and real biological model imports.

### 7.1 Real model processing

| Model | Identifier | Validation |
|---|---|---|
| Hynne2001 glycolysis | BIOMD0000000061 | Successfully imported and rendered |
| Sass2009 alpha-synuclein | BIOMD0000000575 | Successfully parsed, normalized, converted to graph, and rendered |

The alpha-synuclein model produced a graph containing 134 nodes and 332 edges, including 58 reaction nodes and 132 modifier edges.

### 7.2 Pairwise alignment validation

Representative manual validation cases include:

| Capability | Observed result |
|---|---|
| DNA global alignment | Successful |
| Longer DNA global alignment | Score 172, 100 alignment positions |
| Local alignment | Score 50, 25 positions, 100% identity |
| Affine gap alignment | Successful |
| Invalid DNA symbols | Rejected |
| Incompatible DNA/RNA types | Rejected |
| BLOSUM62 with DNA | Rejected |

### 7.3 Automated testing and build verification

- Pairwise alignment API tests: 10 passed.
- Frontend production build: successful.
- Real SBML workflow: successfully executed on the tested models.
- Manual frontend validation: successful for the tested pathway and alignment workflows.

These results demonstrate functional progress. Formal performance benchmarking, exhaustive standards compliance, and large-scale biological dataset evaluation remain future work.

## 8. Implementation Status and Outstanding Work

| Area | Current status |
|---|---|
| Application foundation | Implemented |
| Biological domain models | Implemented within current scope |
| SBML ingestion | Implemented within supported subset |
| Pathway normalization | Implemented |
| Reaction graph construction | Implemented |
| Pathway layouts | Implemented |
| Interactive pathway visualization | Implemented |
| Real BioModels validation | Demonstrated |
| FASTA ingestion | Implemented |
| Pairwise sequence alignment | Implemented |
| Pairwise alignment API | Implemented |
| Sequence Alignment frontend | Implemented |
| Multiple sequence alignment | Not yet implemented |
| Protein structure parsing | Not yet implemented |
| 3D protein visualization | Not yet implemented |
| Synchronized MSA and structure visualization | Not yet implemented |
| Full SBML package coverage | Not yet implemented |
| SBGN integration | Planned |
| UNICON integration | Planned |
| External biological database adapters | Planned |
| AI-assisted biological analysis | Future research direction |

## 9. Future Development

The planned development is divided into several connected directions.

### 9.1 Improve Project 22 capabilities

- Expand SBML coverage.
- Improve graph visualization and interaction.
- Improve support for large pathway networks.
- Investigate SBGN-compatible representations.
- Explore UNICON-related integration.
- Develop adapters for additional biological resources.
- Add more real-world model validation cases.
- Conduct formal layout evaluation.

### 9.2 Complete the sequence-analysis foundation

- Implement multiple sequence alignment.
- Add MSA-specific visualization.
- Improve handling of larger sequence collections.
- Extend alignment analysis and reporting.

### 9.3 Develop Project 9 structural capabilities

- Introduce protein structure parsing.
- Establish structural domain models.
- Implement 3D protein visualization.
- Map sequence positions to structural residues.
- Connect alignment columns to structure views.
- Develop synchronized MSA and 3D exploration.

### 9.4 Connect the biological representations

A longer-term objective is to establish meaningful connections between pathway entities, sequences, and protein structures.

This could allow users to move from a pathway reaction to relevant biological entities and eventually to sequence and structural information where such relationships are available.

Such cross-domain navigation will require reliable biological identifiers, mapping services, and data integration.

It is therefore a future architectural and scientific development objective rather than a current capability.

## 10. Collaboration and Interoperability

Aditi is intended to develop in an open and collaborative manner.

The repository provides a place for source code, implementation details, tests, and technical documentation.

Potential areas for collaboration include:

- SBML parser and normalization improvements.
- Pathway graph representation.
- Biological visualization.
- Layout algorithms.
- MSA implementation.
- Protein structure visualization.
- Sequence-to-structure mapping.
- Biological database integration.
- Interoperability and standards support.

Feedback from the Open Pathway Maps collaborators is particularly valuable for evaluating the pathway architecture and its compatibility with the broader project direction.

Similarly, collaboration with the Project 9 community can help guide the sequence and structural extensions.

The intention is to align implementation decisions with existing community work wherever possible rather than independently duplicating established tools.

## 11. Software and Repository

The Aditi repository is available at:

https://github.com/elixir2026-project22/aditi

The repository contains:

- Backend implementation.
- Frontend implementation.
- Biological domain models.
- Data parsers and normalization.
- Processing workflows.
- API services.
- Tests.
- Technical documentation.

The software is licensed under the MIT License.

The project report and this progress document are intended to provide a transparent record of the current implementation and planned development.

## 12. Conclusion

Aditi has developed into a working prototype with a functional pathway visualization pipeline and a foundational pairwise sequence-analysis workflow.

Its strongest current contribution is the implementation of an SBML-based pathway-processing workflow, from parsing and normalization through graph construction, layout, and interactive visualization. The workflow has been tested with real BioModels examples.

The addition of biological sequence representation, FASTA ingestion, and pairwise alignment extends the platform toward a broader biological analysis environment.

Project 22 provides the primary pathway-visualization direction, while Project 9 provides a complementary longer-term direction for multiple sequence alignment and synchronized protein structure exploration.

The immediate priority is to strengthen the implemented capabilities, improve interoperability, and develop the missing sequence and structural components incrementally.

The long-term vision is a unified and modular biological visualization platform that allows researchers to explore pathway, sequence, and structural information through connected workflows.

Aditi is still under active development, and the current repository represents the implemented foundation on which this broader direction can be built.