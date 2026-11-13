
from __future__ import annotations

from typing import TypeAlias

from aditi.domain.sequences.alignment import (
    AlignedSequence,
    AlignmentResult,
    AlignmentScore,
    AlignmentType,
)
from aditi.domain.sequences.biological_sequence import BiologicalSequence
from aditi.modules.sequence_alignment.scoring.gap_penalty import (
    AffineGapPenalty,
    GapPenalty,
    LinearGapPenalty,
)
from aditi.modules.sequence_alignment.scoring.scoring_scheme import (
    ScoringScheme,
    SimpleScoringScheme,
    SubstitutionScoringScheme,
)


_State: TypeAlias = str

_MATCH = "M"
_GAP_IN_SECOND = "X"
_GAP_IN_FIRST = "Y"


class SmithWaterman:
    """
    Performs local pairwise sequence alignment.

    Uses three dynamic-programming states:

    - M: alignment of two biological residues.
    - X: a residue from the first sequence aligned to a gap.
    - Y: a gap aligned to a residue from the second sequence.

    Unlike global alignment, local alignment allows the optimal
    alignment to begin and end at arbitrary sequence positions.

    Supports both linear and affine gap penalties.
    """

    def align(
        self,
        first_sequence: BiologicalSequence,
        second_sequence: BiologicalSequence,
        scoring_scheme: ScoringScheme,
        gap_penalty: GapPenalty,
    ) -> AlignmentResult:
        """Locally align the highest-scoring regions of two sequences."""

        self._validate_inputs(
            first_sequence,
            second_sequence,
            scoring_scheme,
            gap_penalty,
        )

        first = first_sequence.residues
        second = second_sequence.residues

        first_length = len(first)
        second_length = len(second)

        gap_open, gap_extension = self._gap_parameters(
            gap_penalty,
        )

        match_scores = [
            [0.0] * (second_length + 1)
            for _ in range(first_length + 1)
        ]

        gap_second_scores = [
            [0.0] * (second_length + 1)
            for _ in range(first_length + 1)
        ]

        gap_first_scores = [
            [0.0] * (second_length + 1)
            for _ in range(first_length + 1)
        ]

        match_trace: list[list[_State | None]] = [
            [None] * (second_length + 1)
            for _ in range(first_length + 1)
        ]

        gap_second_trace: list[list[_State | None]] = [
            [None] * (second_length + 1)
            for _ in range(first_length + 1)
        ]

        gap_first_trace: list[list[_State | None]] = [
            [None] * (second_length + 1)
            for _ in range(first_length + 1)
        ]

        best_score = 0.0
        best_i = 0
        best_j = 0
        best_state: _State | None = None

        for i in range(1, first_length + 1):
            for j in range(1, second_length + 1):
                substitution_score = scoring_scheme.score(
                    first[i - 1],
                    second[j - 1],
                )

                # Match / mismatch state.
                match_candidates = (
                    (
                        match_scores[i - 1][j - 1]
                        + substitution_score,
                        _MATCH,
                    ),
                    (
                        gap_second_scores[i - 1][j - 1]
                        + substitution_score,
                        _GAP_IN_SECOND,
                    ),
                    (
                        gap_first_scores[i - 1][j - 1]
                        + substitution_score,
                        _GAP_IN_FIRST,
                    ),
                )

                match_score, previous_match_state = self._best(
                    match_candidates,
                )

                if match_score > 0.0:
                    match_scores[i][j] = match_score
                    match_trace[i][j] = previous_match_state

                    if match_score > best_score:
                        best_score = match_score
                        best_i = i
                        best_j = j
                        best_state = _MATCH

                # Residue from the first sequence aligned to a gap.
                #
                # A gap can extend from its own state or open from
                # the match state. Direct transitions between
                # opposing gap states are intentionally disallowed.
                gap_second_candidates = (
                    (
                        gap_second_scores[i - 1][j]
                        + gap_extension,
                        _GAP_IN_SECOND,
                    ),
                    (
                        match_scores[i - 1][j]
                        + gap_open,
                        _MATCH,
                    ),
                )

                gap_second_score, previous_gap_second_state = (
                    self._best(gap_second_candidates)
                )

                if gap_second_score > 0.0:
                    gap_second_scores[i][j] = gap_second_score
                    gap_second_trace[i][j] = (
                        previous_gap_second_state
                    )

                # Gap in the first sequence aligned to a residue
                # from the second sequence.
                gap_first_candidates = (
                    (
                        gap_first_scores[i][j - 1]
                        + gap_extension,
                        _GAP_IN_FIRST,
                    ),
                    (
                        match_scores[i][j - 1]
                        + gap_open,
                        _MATCH,
                    ),
                )

                gap_first_score, previous_gap_first_state = (
                    self._best(gap_first_candidates)
                )

                if gap_first_score > 0.0:
                    gap_first_scores[i][j] = gap_first_score
                    gap_first_trace[i][j] = (
                        previous_gap_first_state
                    )

        if best_state is None:
            raise ValueError(
                "No positive-scoring local alignment exists "
                "for the supplied sequences and scoring parameters."
            )

        aligned_first, aligned_second, first_mapping, second_mapping = (
            self._traceback(
                first,
                second,
                match_trace,
                gap_second_trace,
                gap_first_trace,
                best_i,
                best_j,
                best_state,
            )
        )

        first_result = AlignedSequence(
            sequence_identity=first_sequence.identity,
            residues="".join(aligned_first),
            position_mapping=tuple(first_mapping),
        )

        second_result = AlignedSequence(
            sequence_identity=second_sequence.identity,
            residues="".join(aligned_second),
            position_mapping=tuple(second_mapping),
        )

        identical_positions = sum(
            first_residue == second_residue
            and first_residue != "-"
            for first_residue, second_residue in zip(
                first_result.residues,
                second_result.residues,
            )
        )

        alignment_score = self._build_alignment_score(
            best_score,
            scoring_scheme,
            gap_penalty,
        )

        return AlignmentResult(
            aligned_sequences=(
                first_result,
                second_result,
            ),
            alignment_type=AlignmentType.LOCAL,
            score=alignment_score,
            identical_positions=identical_positions,
        )

    @staticmethod
    def _traceback(
        first: str,
        second: str,
        match_trace: list[list[_State | None]],
        gap_second_trace: list[list[_State | None]],
        gap_first_trace: list[list[_State | None]],
        start_i: int,
        start_j: int,
        start_state: _State,
    ) -> tuple[
        list[str],
        list[str],
        list[int | None],
        list[int | None],
    ]:
        """Trace the optimal local alignment back to its start."""

        aligned_first: list[str] = []
        aligned_second: list[str] = []

        first_mapping: list[int | None] = []
        second_mapping: list[int | None] = []

        i = start_i
        j = start_j
        state = start_state

        while True:
            if state == _MATCH:
                if i == 0 or j == 0:
                    break

                previous_state = match_trace[i][j]

                if previous_state is None:
                    break

                aligned_first.append(first[i - 1])
                aligned_second.append(second[j - 1])

                first_mapping.append(i - 1)
                second_mapping.append(j - 1)

                i -= 1
                j -= 1

            elif state == _GAP_IN_SECOND:
                if i == 0:
                    break

                previous_state = gap_second_trace[i][j]

                if previous_state is None:
                    break

                aligned_first.append(first[i - 1])
                aligned_second.append("-")

                first_mapping.append(i - 1)
                second_mapping.append(None)

                i -= 1

            elif state == _GAP_IN_FIRST:
                if j == 0:
                    break

                previous_state = gap_first_trace[i][j]

                if previous_state is None:
                    break

                aligned_first.append("-")
                aligned_second.append(second[j - 1])

                first_mapping.append(None)
                second_mapping.append(j - 1)

                j -= 1

            else:
                raise RuntimeError(
                    f"Unknown traceback state: {state!r}."
                )

            state = previous_state

        aligned_first.reverse()
        aligned_second.reverse()

        first_mapping.reverse()
        second_mapping.reverse()

        if not aligned_first:
            raise RuntimeError(
                "Local alignment traceback produced an empty alignment."
            )

        return (
            aligned_first,
            aligned_second,
            first_mapping,
            second_mapping,
        )

    @staticmethod
    def _validate_inputs(
        first_sequence: BiologicalSequence,
        second_sequence: BiologicalSequence,
        scoring_scheme: ScoringScheme,
        gap_penalty: GapPenalty,
    ) -> None:
        if not isinstance(first_sequence, BiologicalSequence):
            raise TypeError(
                "First input must be a BiologicalSequence."
            )

        if not isinstance(second_sequence, BiologicalSequence):
            raise TypeError(
                "Second input must be a BiologicalSequence."
            )

        if first_sequence.alphabet is not second_sequence.alphabet:
            raise ValueError(
                "Both sequences must use the same biological alphabet."
            )

        if not isinstance(scoring_scheme, ScoringScheme):
            raise TypeError(
                "Scoring scheme must implement ScoringScheme."
            )

        if scoring_scheme.alphabet is not first_sequence.alphabet:
            raise ValueError(
                "Scoring scheme alphabet must match the sequence alphabet."
            )

        if not isinstance(gap_penalty, GapPenalty):
            raise TypeError(
                "Gap penalty must implement GapPenalty."
            )

    @staticmethod
    def _gap_parameters(
        gap_penalty: GapPenalty,
    ) -> tuple[float, float]:
        if isinstance(gap_penalty, LinearGapPenalty):
            return (
                gap_penalty.gap_penalty,
                gap_penalty.gap_penalty,
            )

        if isinstance(gap_penalty, AffineGapPenalty):
            return (
                gap_penalty.gap_open_penalty,
                gap_penalty.gap_extension_penalty,
            )

        raise TypeError(
            "Unsupported gap penalty implementation."
        )

    @staticmethod
    def _best(
        candidates: tuple[tuple[float, _State], ...],
    ) -> tuple[float, _State]:
        """Select the highest score, preserving candidate order on ties."""

        best_score, best_state = candidates[0]

        for score, state in candidates[1:]:
            if score > best_score:
                best_score = score
                best_state = state

        return best_score, best_state

    @staticmethod
    def _build_alignment_score(
        score: float,
        scoring_scheme: ScoringScheme,
        gap_penalty: GapPenalty,
    ) -> AlignmentScore:
        if isinstance(gap_penalty, LinearGapPenalty):
            gap_open = gap_penalty.gap_penalty
            gap_extension = gap_penalty.gap_penalty
        else:
            gap_open = gap_penalty.gap_open_penalty
            gap_extension = gap_penalty.gap_extension_penalty

        if isinstance(scoring_scheme, SimpleScoringScheme):
            return AlignmentScore(
                score=score,
                scoring_scheme="simple",
                gap_open_penalty=gap_open,
                gap_extension_penalty=gap_extension,
                match_score=scoring_scheme.match_score,
                mismatch_score=scoring_scheme.mismatch_score,
            )

        if isinstance(scoring_scheme, SubstitutionScoringScheme):
            return AlignmentScore(
                score=score,
                scoring_scheme="substitution_matrix",
                gap_open_penalty=gap_open,
                gap_extension_penalty=gap_extension,
                substitution_matrix=scoring_scheme.matrix_name,
            )

        raise TypeError(
            "Unsupported scoring scheme implementation."
        )
