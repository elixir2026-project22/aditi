# Aditi — Unified Biological Pathway and Molecular Visualization Platform

> **Project:** Europe BioHackathon  
> **Foundation:** Project 22 — Open Pathway Maps: Scalable and FAIR Visualization of Metabolic Networks  
> **Extension:** Project 9 — From Alignment to Insight: Synchronized MSA and 3D Structure Visualization  
> **Architecture:** Modular, Actor-Oriented Runtime  
> **Status:** Initial Architecture and Project Foundation  
> **Working Name:** Aditi

---

# 1. Project Overview

Aditi is an open-source, modular biological visualization and analysis platform designed to connect metabolic pathway representations, biological sequence information, and three-dimensional molecular structures within a unified runtime environment.

The project combines two complementary BioHackathon problem statements into a layered architecture.

The first layer focuses on the scalable and FAIR visualization of metabolic pathways. It addresses the challenges of representing biochemical networks in biologically meaningful, structured, machine-readable formats that support reuse, interoperability, and downstream scientific analysis.

The second layer extends this foundation by connecting multiple sequence alignments (MSA) with three-dimensional protein structures. It enables users to investigate how sequence conservation and divergence correspond to molecular structure and surface features through synchronized 1D and 3D visualization.

Rather than developing two independent applications, Aditi aims to provide a common runtime where pathway representations, biological entities, sequence alignments, and molecular structures can be loaded, processed, related, and visualized through independent modules.

The platform should remain extensible so that additional biological data sources, visualization techniques, and analytical capabilities can be integrated without restructuring the entire application.

# 2. Problem Statements

## 2.1 Foundation Layer — Project 22

**Open Pathway Maps: Scalable and FAIR Visualization of Metabolic Networks**

Existing metabolic pathway resources contain extensive curated biochemical knowledge. However, producing biologically meaningful pathway maps remains cumbersome, while licensing restrictions in some established resources limit open access and reuse.

Aditi's foundation layer addresses this through:

- Evaluation and benchmarking of existing pathway layout strategies.
- Graph-based layout methods.
- Constraint-based approaches, including UNICON.
- Standards-aware representations based on SBML and SBGN.
- Biological and visual requirements for pathway maps.
- Reusable, structured, machine-readable pathway representations.
- FAIR principles and interoperability with research infrastructures.

Representative reference resources include:

- BRENDA
- Reactome
- Metabolic Atlas
- Other openly accessible pathway resources.

The resulting pathway representations should support downstream scientific workflows, including omics data integration.

The architecture should also leave room for integration with sustainable research infrastructures such as the DSMZ Digital Diversity Hub, Metabolic Atlas, and ELIXIR Node services.

## 2.2 Extension Layer — Project 9

**From Alignment to Insight: Synchronized MSA and 3D Structure Visualization**

The second layer connects multiple sequence alignments with three-dimensional protein structures.

A multiple sequence alignment contains information about conserved and divergent sequence positions. However, interpreting those positions in a structural context often requires switching between specialized tools and manually understanding structural relationships.

Aditi's second layer aims to connect these representations directly.

Its capabilities include:

- Loading standard MSA files in FASTA and CLUSTALW formats.
- Loading associated protein structures.
- Mapping alignment positions to structural residues.
- Displaying conservation and divergence in a molecular context.
- Synchronizing the 1D alignment view with the 3D molecular view.
- Highlighting conserved regions and divergent structural surfaces.
- Supporting ensemble comparison across GPCRs, Tyrosine Kinases, and Immunoglobulins.
- Providing a reusable surface-mapping API.
- Supporting LLM-assisted alignment, analysis, and reporting.

The implementation should build on the Mol*/iCn3D MolViewSpec bridge from BioHackathon Europe 2025 where applicable.

# 3. Core Architectural Vision

Aditi is designed as a **unified biological visualization runtime**, not a collection of tightly coupled visualization components.

The application is divided into independently managed modules. Each module owns a particular domain of functionality and communicates through defined interfaces and events.

The central runtime is responsible for:

- Application lifecycle.
- Module registration and initialization.
- Dependency resolution.
- Data-source management.
- Event distribution.
- Shared biological entity identification.
- Resource and cache management.
- Visualization coordination.
- Logging and error handling.

Individual modules should not directly control the internal implementation of other modules.

For example:

- The Pathway Module should not depend on the internal rendering implementation of the Molecular Visualization Module.
- The MSA Module should not directly manipulate the molecular viewer's internal data structures.
- The Structure Module should not need to know how pathway layouts are calculated.
- The Visualization Runtime should coordinate presentation without owning biological domain logic.

Modules should communicate through shared data contracts, identifiers, events, and explicitly defined service interfaces.

# 4. System Architecture

The application is organized into five major architectural layers.

```text
                    ADITI APPLICATION
                           |
                           v
                 APPLICATION RUNTIME
                           |
          +----------------+----------------+
          |                |                |
          v                v                v
     MODULE MANAGER   EVENT SYSTEM    RESOURCE MANAGER
          |                |                |
          +----------------+----------------+
                           |
                           v
                 BIOLOGICAL DATA LAYER
                           |
          +----------------+----------------+
          |                |                |
          v                v                v
    PATHWAY DATA      SEQUENCE DATA     STRUCTURE DATA
          |                |                |
          +----------------+----------------+
                           |
                           v
                 BIOLOGICAL ENTITY LAYER
                           |
          +----------------+----------------+
          |                |                |
          v                v                v
     PATHWAY MODEL     MSA MODEL       STRUCTURE MODEL
          |                |                |
          +----------------+----------------+
                           |
                           v
                  ANALYSIS LAYER
                           |
          +----------------+----------------+
          |                |                |
          v                v                v
      PATHWAY LAYOUT   MSA MAPPING    STRUCTURAL MAPPING
          |                |                |
          +----------------+----------------+
                           |
                           v
                  VISUALIZATION LAYER
                           |
          +----------------+----------------+
          |                |                |
          v                v                v
     PATHWAY VIEW      MSA VIEW       MOLECULAR VIEW
                           |
                           v
                SYNCHRONIZED INTERACTION
```

This is a logical architecture. The actual implementation can distribute responsibilities across processes or threads where necessary, but independent module boundaries should remain consistent.

# 5. Modular Runtime Architecture

## 5.1 Application Core

**Responsibility:** Own the application's lifecycle and provide the base runtime environment.

Components:

- Application Launcher
- Application Context
- Configuration Manager
- Module Manager
- Dependency Resolver
- Event Dispatcher
- Resource Manager
- Logging System
- Error Handler

The Application Core should not contain pathway-specific, sequence-specific, or molecular visualization logic.

It provides the infrastructure required to initialize and coordinate the rest of the application.

## 5.2 Module Manager

**Responsibility:** Manage independent application modules.

Every module should expose a common lifecycle contract.

Conceptually:

```text
Module
 ├── Register()
 ├── Initialize(Context)
 ├── Start()
 ├── Update(DeltaTime)
 ├── Stop()
 └── Shutdown()
```

The Module Manager should:

- Register available modules.
- Validate module dependencies.
- Resolve initialization order.
- Initialize modules.
- Start and stop modules.
- Handle module failures.
- Release module-owned resources.

A module should be independently replaceable where its interface remains compatible.

Modules should declare their dependencies explicitly rather than relying on hidden initialization order.

## 5.3 Actor-Oriented Module Communication

Aditi uses an actor-oriented communication model.

Each major subsystem owns its internal state and processes incoming commands or events through a defined interface.

A module should not directly modify another module's internal state.

Instead, communication should follow a message-based model:

```text
Module A
   |
   | Command / Event
   v
Event Dispatcher
   |
   | Routed Message
   v
Module B
   |
   | Result / Event
   v
Event Dispatcher
   |
   v
Module A or Other Subscribers
```

Example:

```text
User selects a protein
        |
        v
Biological Entity Registry
        |
        v
Structure Resolution Request
        |
        v
Structure Data Module
        |
        v
Structure Retrieved
        |
        v
Molecular Visualization Module
        |
        v
3D Structure Displayed
```

The event system should support:

- Commands for requesting operations.
- Events for announcing completed operations or state changes.
- Responses for returning operation results.
- Correlation identifiers for tracking asynchronous operations.
- Error messages for failed operations.
- Cancellation where long-running operations support it.

A command represents a request to perform work. An event represents something that has already happened.

The actor-oriented design should not require every module to run in a separate operating-system process. Modules can initially run within one application process while retaining independent ownership and message-based boundaries.

# 6. Biological Data Architecture

## 6.1 Data Source Manager

**Responsibility:** Provide a common interface for external biological resources.

The Data Source Manager coordinates adapters for different resources.

Initial integrations:

| Resource | Primary purpose |
|---|---|
| BRENDA | Enzyme and biochemical information |
| Reactome | Biological pathways and reactions |
| Metabolic Atlas | Metabolic pathway representations |
| RCSB PDB | Protein structure information |
| Other open resources | Additional biological data |

The manager should support:

- Source registration.
- Source-specific adapters.
- Request routing.
- Data retrieval.
- Response validation.
- Provenance tracking.
- Caching.
- Source availability and error reporting.

External resources should be accessed through adapters rather than directly from visualization modules.

## 6.2 Data Normalization

Different biological resources may use different identifiers, formats, naming conventions, and representations.

The normalization layer should convert incoming information into Aditi's internal data contracts.

Responsibilities:

- Identifier normalization.
- Data format conversion.
- Validation.
- Metadata extraction.
- Relationship resolution.
- Source provenance.
- Duplicate detection where possible.

The original source information should remain traceable.

Normalization must not silently imply that two biological entities are identical when the source data does not establish that relationship.

## 6.3 Biological Entity Registry

**Responsibility:** Maintain a common identity and relationship layer across biological modules.

The registry provides stable internal references to biological entities.

Initial entity types:

```text
BiologicalEntity
 ├── Pathway
 ├── Reaction
 ├── Enzyme
 ├── Protein
 ├── Gene
 ├── Metabolite
 ├── Sequence
 ├── MolecularStructure
 └── BiologicalComplex
```

The registry should maintain:

- Internal identifiers.
- External identifiers.
- Entity type.
- Source references.
- Metadata.
- Known relationships.
- Data provenance.

It should allow different modules to refer to the same biological entity without sharing their internal implementation.

# 7. Functional Modules

## 7.1 Pathway Data Module

**Layer:** Project 22

**Responsibility:** Retrieve, validate, and represent metabolic pathway information.

Capabilities:

- Import pathway data.
- Parse supported pathway formats.
- Retrieve pathway metadata.
- Resolve biological entities.
- Represent reactions and relationships.
- Export structured pathway representations.

The module should expose a normalized pathway model to the rest of the application.

## 7.2 Pathway Layout Engine

**Layer:** Project 22

**Responsibility:** Generate biologically meaningful pathway layouts.

The layout engine should be independent of the pathway viewer.

Potential strategies:

- Graph-based layout.
- Constraint-based layout.
- UNICON-based approaches.
- SBML-aware processing.
- SBGN-aware representation.

The architecture should support benchmarking different layout strategies against representative reference pathways.

Layout output should preserve the biological relationships of the input model.

The layout engine should expose a common interface so additional strategies can be introduced without changing the Pathway Visualization Module.

## 7.3 Pathway Visualization Module

**Layer:** Project 22

**Responsibility:** Display metabolic pathways and support interactive exploration.

Capabilities:

- Pathway rendering.
- Node and reaction visualization.
- Interactive navigation.
- Entity selection.
- Metadata inspection.
- Pathway layout updates.
- Export and representation inspection.

The visualization module should consume pathway models and layout results rather than performing data retrieval or biological interpretation itself.

## 7.4 Sequence and MSA Module

**Layer:** Project 9

**Responsibility:** Load and represent multiple sequence alignments.

Initial supported formats:

- FASTA.
- CLUSTALW.

Capabilities:

- MSA parsing.
- Sequence identification.
- Alignment-column representation.
- Conservation analysis.
- Divergence analysis.
- Sequence-to-protein mapping.
- Alignment navigation.

The module should expose alignment information independently of the user interface.

## 7.5 Protein Structure Module

**Layer:** Project 9

**Responsibility:** Retrieve, load, and manage protein structures.

Capabilities:

- Structure retrieval.
- Structure file parsing.
- Structure metadata.
- Chain identification.
- Residue identification.
- Structure-to-sequence mapping.
- Structure ensemble management.

Structure retrieval and structure rendering should remain separate responsibilities.

The module should preserve structure provenance and the identifiers used to retrieve each structure.

## 7.6 Alignment-to-Structure Mapping Module

**Layer:** Project 9

**Responsibility:** Connect MSA positions to residues in protein structures.

This is a central integration component of Project 9.

Capabilities:

- Map alignment positions to sequence positions.
- Map sequence positions to structural residues.
- Handle gaps in alignments.
- Handle missing structural residues.
- Validate mappings.
- Produce reusable mapping results.

The mapping engine should not depend on the molecular viewer or the MSA user interface.

Its output should be a reusable mapping representation consumed by visualization and analysis modules.

## 7.7 Molecular Visualization Module

**Layer:** Project 9

**Responsibility:** Display protein structures in an interactive 3D environment.

The implementation should investigate the Mol*/iCn3D MolViewSpec bridge established in BioHackathon Europe 2025.

Capabilities:

- 3D protein visualization.
- Molecular surface visualization.
- Residue selection.
- Chain selection.
- Conservation mapping.
- Divergence mapping.
- Structure ensemble comparison.

The viewer should expose interaction interfaces to the synchronization system without exposing its entire internal rendering implementation.

## 7.8 Synchronization Module

**Layer:** Project 9

**Responsibility:** Keep the MSA representation and molecular representation synchronized.

This module connects the one-dimensional alignment view with the three-dimensional molecular view.

Example interaction:

```text
User selects an MSA column
          |
          v
MSA Selection Event
          |
          v
Alignment-to-Structure Mapping
          |
          v
Mapped Residues
          |
          v
Molecular Selection Event
          |
          v
3D Structure Highlights Corresponding Residues
```

Reverse interaction:

```text
User selects a molecular residue
          |
          v
Molecular Selection Event
          |
          v
Structure-to-Sequence Mapping
          |
          v
Corresponding MSA Position
          |
          v
MSA View Highlights Alignment Column
```

The synchronization module should coordinate selection and highlighting without owning the rendering logic of either viewer.

## 7.9 Analysis Module

**Layer:** Shared infrastructure

**Responsibility:** Provide reusable biological analysis operations.

Potential capabilities:

- Conservation analysis.
- Divergence analysis.
- Pathway relationship inspection.
- Structural region analysis.
- Comparative structure analysis.
- Biological metadata aggregation.

Analysis modules should produce structured results that can be consumed by multiple visualization modules.

## 7.10 AI Assistance Module

**Layer:** Optional extension

**Responsibility:** Assist users in understanding and interpreting biological information.

Potential capabilities:

- Natural-language queries.
- Alignment explanation.
- Analysis summaries.
- Biological report generation.
- Contextual explanations of selected regions.
- Assistance in navigating biological entities.

AI-generated interpretations should remain distinguishable from source-derived biological data and deterministic analytical results.

AI should not silently modify pathway data, alignment mappings, or molecular structures.

# 8. Shared Data Contracts

The modules should communicate through stable data contracts.

Initial conceptual models:

```text
BiologicalEntity
Pathway
PathwayNode
PathwayReaction
PathwayRelationship

Sequence
SequenceAlignment
AlignmentColumn
AlignmentPosition

Protein
ProteinChain
ProteinResidue
MolecularStructure
StructureEnsemble

AlignmentStructureMapping
ConservationResult
DivergenceResult

VisualizationState
SelectionState
DataSource
DataProvenance
AnalysisResult
```

Each model should have a clearly defined owner.

For example:

- The Pathway Data Module owns pathway parsing and normalized pathway data.
- The MSA Module owns alignment parsing and alignment representations.
- The Structure Module owns structure loading and structure representations.
- The Mapping Module owns alignment-to-structure correspondence results.
- The Synchronization Module owns cross-view selection coordination.

Other modules should access these models through defined interfaces.

# 9. Runtime Execution Flow

## 9.1 Application Initialization

```text
Application Launcher
        |
        v
Application Core
        |
        v
Load Configuration
        |
        v
Initialize Event Dispatcher
        |
        v
Initialize Resource Manager
        |
        v
Register Modules
        |
        v
Resolve Dependencies
        |
        v
Initialize Modules
        |
        v
Start Application Runtime
        |
        v
Ready for User Interaction
```

## 9.2 Project 22 Runtime Flow

```text
User Requests Pathway
        |
        v
Pathway Data Module
        |
        v
Data Source Manager
        |
        v
External Pathway Resource
        |
        v
Data Normalization
        |
        v
Biological Entity Registry
        |
        v
Pathway Model
        |
        v
Pathway Layout Engine
        |
        v
Layout Result
        |
        v
Pathway Visualization
```

## 9.3 Project 9 Runtime Flow

```text
User Loads MSA and Structure
        |
        v
MSA Module + Structure Module
        |
        v
Sequence and Structure Validation
        |
        v
Alignment-to-Structure Mapping
        |
        v
Conservation / Divergence Analysis
        |
        v
Synchronization Module
        |
        v
MSA Visualization + Molecular Visualization
        |
        v
Synchronized Biological Exploration
```

# 10. FAIR and Interoperability Requirements

FAIR principles should be considered throughout the architecture.

**Findable**
- Maintain stable identifiers.
- Preserve external source references.
- Provide searchable biological entities and metadata.

**Accessible**
- Prefer open and accessible data resources.
- Provide documented data access interfaces.
- Preserve information about source availability and restrictions.

**Interoperable**
- Support appropriate standards such as SBML and SBGN.
- Support standard MSA formats such as FASTA and CLUSTALW.
- Maintain explicit relationships between sequence and structural identifiers.
- Provide machine-readable representations.

**Reusable**
- Preserve provenance.
- Document data transformations.
- Keep representations structured.
- Provide reusable APIs and export interfaces.

# 11. Proposed Repository Structure

```text
Aditi/
│
├── README.md
├── LICENSE
├── CONTRIBUTING.md
├── docs/
│   ├── architecture/
│   ├── module-contracts/
│   ├── data-models/
│   └── development/
│
├── application/
│   ├── Core/
│   ├── Runtime/
│   ├── ModuleManager/
│   ├── DependencyResolver/
│   ├── EventSystem/
│   ├── ResourceManager/
│   └── Configuration/
│
├── domain/
│   ├── BiologicalEntities/
│   ├── Pathways/
│   ├── Sequences/
│   ├── Structures/
│   └── Relationships/
│
├── modules/
│   │
│   ├── Project22/
│   │   ├── PathwayData/
│   │   ├── PathwayLayout/
│   │   ├── LayoutBenchmark/
│   │   └── PathwayVisualization/
│   │
│   ├── Project09/
│   │   ├── MSA/
│   │   ├── ProteinStructure/
│   │   ├── AlignmentMapping/
│   │   ├── MolecularVisualization/
│   │   └── Synchronization/
│   │
│   └── Shared/
│       ├── Analysis/
│       ├── AI/
│       └── BiologicalEntityRegistry/
│
├── data/
│   ├── DataSourceManager/
│   ├── Adapters/
│   │   ├── BRENDA/
│   │   ├── Reactome/
│   │   ├── MetabolicAtlas/
│   │   └── RCSB_PDB/
│   ├── Normalization/
│   ├── Validation/
│   ├── Provenance/
│   └── Cache/
│
├── visualization/
│   ├── VisualizationRuntime/
│   ├── SharedInterfaces/
│   └── Interaction/
│
├── api/
│   ├── PathwayAPI/
│   ├── MappingAPI/
│   └── VisualizationAPI/
│
├── infrastructure/
│   ├── Logging/
│   ├── Storage/
│   ├── Networking/
│   └── Monitoring/
│
├── tests/
│   ├── Unit/
│   ├── Integration/
│   ├── Module/
│   ├── Mapping/
│   └── Validation/
│
├── resources/
│   ├── datasets/
│   ├── reference-pathways/
│   ├── reference-alignments/
│   └── reference-structures/
│
├── scripts/
│
└── config/
    ├── application/
    ├── modules/
    └── data-sources/
```

This is a logical starting structure. Physical project boundaries can be adjusted to the selected programming language and framework.

# 12. Development Phases

## Phase 0 — Runtime Foundation

- Establish the application core.
- Define module lifecycle contracts.
- Implement module registration and dependency resolution.
- Implement message and event communication.
- Establish logging and configuration.
- Define shared biological data contracts.

**Expected result:** An executable runtime capable of loading and coordinating independent modules.

## Phase 1 — Project 22: Pathway Data Foundation

- Implement pathway data models.
- Establish data-source adapter interfaces.
- Integrate an initial open pathway resource.
- Implement normalization and validation.
- Register biological entities.
- Load a representative pathway.

**Expected result:** A pathway can be retrieved, normalized, and represented internally.

## Phase 2 — Project 22: Pathway Layout and Visualization

- Implement the layout engine interface.
- Integrate an initial graph-based layout strategy.
- Investigate constraint-based approaches, including UNICON.
- Investigate SBML and SBGN-aware processing.
- Build the pathway viewer.
- Establish reference cases for layout benchmarking.

**Expected result:** A pathway can be visualized and its representation exported in a structured format.

## Phase 3 — Project 9: MSA and Structure Foundation

- Implement FASTA parsing.
- Implement CLUSTALW parsing.
- Establish sequence and protein models.
- Integrate structure retrieval.
- Load protein structures.
- Establish sequence-to-structure correspondence.

**Expected result:** An alignment and its associated protein structures can be loaded and represented.

## Phase 4 — Project 9: Synchronized Visualization

- Implement alignment-to-structure mapping.
- Implement conservation and divergence analysis.
- Integrate molecular surface visualization.
- Implement MSA-to-3D selection synchronization.
- Implement reverse 3D-to-MSA selection.
- Validate mapping behavior against representative proteins.

**Expected result:** Selecting an alignment position highlights the corresponding structural region, and selecting a structural region highlights the corresponding alignment position.

## Phase 5 — Unified Biological Exploration

- Connect pathway entities with the shared biological entity registry.
- Integrate pathway and protein navigation where identifiers and source data establish valid relationships.
- Add reusable analysis interfaces.
- Add optional AI-assisted analysis and reporting.
- Improve export and interoperability.
- Validate the complete application workflow.

**Expected result:** Aditi operates as a unified biological visualization platform with two integrated functional layers.

# 13. Initial Demonstration Scenarios

## Demonstration A — Open Pathway Maps

1. Load a representative metabolic pathway.
2. Retrieve its source information.
3. Normalize pathway entities and relationships.
4. Generate a pathway layout.
5. Display the pathway.
6. Inspect individual reactions and biological entities.
7. Export the pathway representation.

## Demonstration B — Synchronized MSA and Molecular Structure

1. Load a multiple sequence alignment.
2. Load the associated protein structures.
3. Calculate conservation and divergence.
4. Map alignment positions to structural residues.
5. Display the alignment.
6. Display the molecular structure.
7. Select a conserved alignment region.
8. Highlight the corresponding molecular surface.
9. Select a structural region.
10. Highlight the corresponding alignment positions.

The demonstration should use representative protein families such as GPCRs, Tyrosine Kinases, and Immunoglobulins where suitable reference data is available.

# 14. Engineering Principles

Aditi should follow these architectural principles throughout development.

1. **Modular ownership:** Every module owns its internal implementation and state.
2. **Explicit contracts:** Modules communicate through defined interfaces and data contracts.
3. **Message-based communication:** Cross-module operations use commands, events, and responses.
4. **Independent visualization:** Pathway, alignment, and molecular viewers remain independent components.
5. **Separation of concerns:** Data retrieval, normalization, analysis, mapping, and rendering remain separate responsibilities.
6. **Source traceability:** Biological information retains its original source and provenance.
7. **Standards-first design:** Prefer established biological formats and representations where applicable.
8. **Replaceable implementations:** A module can be replaced without rewriting unrelated modules.
9. **Deterministic analysis:** Biological mappings and calculations should be reproducible and independently testable.
10. **Extensible runtime:** New biological resources, algorithms, and visualization modules should be introduced through defined contracts.

# 15. Scope and Boundaries

Aditi's initial scope is the integration of the two BioHackathon problem statements.

Project 22 establishes the pathway representation, layout, and FAIR data foundation.

Project 9 extends the application with MSA analysis, protein structure mapping, and synchronized 1D/3D visualization.

The project should not initially attempt to become a complete computational biology suite.

In particular:

- Pathway visualization does not automatically imply metabolic flux simulation.
- A sequence alignment does not automatically establish a functional relationship.
- A structural mapping must account for alignment gaps and missing residues.
- A molecular viewer should not imply biological interactions that have not been established by source data or validated analysis.
- AI-generated explanations must remain distinguishable from experimentally supported information.
- External data availability and licensing must be checked before integration or redistribution.

The architecture should make future expansion possible without making every future capability a requirement for the initial implementation.

# 16. Final Project Objective

Aditi aims to establish a unified, open, and modular biological visualization environment in which metabolic pathway representations and protein sequence-to-structure relationships can be explored through a common runtime.

The foundation layer provides scalable, FAIR, machine-readable pathway maps.

The extension layer connects multiple sequence alignments with three-dimensional molecular structures, allowing biological conservation and divergence to be interpreted in structural context.

Together, these layers provide a reusable foundation for biological visualization, scientific exploration, and downstream analysis.

**The central objective is to connect biological representations without coupling their underlying systems.**