
from __future__ import annotations

import math
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
_NEGATIVE_INFINITY = float("-inf")


class NeedlemanWunsch:
    """
    Performs global pairwise sequence alignment.

    Uses three dynamic-programming states:
    - M: alignment of two biological residues.
    - X: a residue from the first sequence aligned to a gap.
    - Y: a gap aligned to a residue from the second sequence.

    This supports both linear and affine gap penalties.
    """

    _MATCH = "M"
    _GAP_IN_SECOND = "X"
    _GAP_IN_FIRST = "Y"

    def align(
        self,
        first_sequence: BiologicalSequence,
        second_sequence: BiologicalSequence,
        scoring_scheme: ScoringScheme,
        gap_penalty: GapPenalty,
    ) -> AlignmentResult:
        """Globally align two complete biological sequences."""

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
            [_NEGATIVE_INFINITY] * (second_length + 1)
            for _ in range(first_length + 1)
        ]

        gap_second_scores = [
            [_NEGATIVE_INFINITY] * (second_length + 1)
            for _ in range(first_length + 1)
        ]

        gap_first_scores = [
            [_NEGATIVE_INFINITY] * (second_length + 1)
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

        match_scores[0][0] = 0.0

        for i in range(1, first_length + 1):
            gap_second_scores[i][0] = (
                gap_open + (i - 1) * gap_extension
            )

            gap_second_trace[i][0] = (
                self._MATCH if i == 1 else self._GAP_IN_SECOND
            )

        for j in range(1, second_length + 1):
            gap_first_scores[0][j] = (
                gap_open + (j - 1) * gap_extension
            )

            gap_first_trace[0][j] = (
                self._MATCH if j == 1 else self._GAP_IN_FIRST
            )

        for i in range(1, first_length + 1):
            for j in range(1, second_length + 1):
                substitution_score = scoring_scheme.score(
                    first[i - 1],
                    second[j - 1],
                )

                best_match, previous_match_state = self._best(
                    (
                        (match_scores[i - 1][j - 1], self._MATCH),
                        (
                            gap_second_scores[i - 1][j - 1],
                            self._GAP_IN_SECOND,
                        ),
                        (
                            gap_first_scores[i - 1][j - 1],
                            self._GAP_IN_FIRST,
                        ),
                    )
                )

                match_scores[i][j] = (
                    best_match + substitution_score
                )

                match_trace[i][j] = previous_match_state

                best_gap_second, previous_gap_second_state = self._best(
                    (
                        (
                            gap_second_scores[i - 1][j] + gap_extension,
                            self._GAP_IN_SECOND,
                        ),
                        (
                            match_scores[i - 1][j] + gap_open,
                            self._MATCH,
                        ),
                        (
                            gap_first_scores[i - 1][j] + gap_open,
                            self._GAP_IN_FIRST,
                        ),
                    )
                )

                gap_second_scores[i][j] = best_gap_second
                gap_second_trace[i][j] = previous_gap_second_state

                best_gap_first, previous_gap_first_state = self._best(
                    (
                        (
                            gap_first_scores[i][j - 1] + gap_extension,
                            self._GAP_IN_FIRST,
                        ),
                        (
                            match_scores[i][j - 1] + gap_open,
                            self._MATCH,
                        ),
                        (
                            gap_second_scores[i][j - 1] + gap_open,
                            self._GAP_IN_SECOND,
                        ),
                    )
                )

                gap_first_scores[i][j] = best_gap_first
                gap_first_trace[i][j] = previous_gap_first_state

        final_score, state = self._best(
            (
                (match_scores[first_length][second_length], self._MATCH),
                (
                    gap_second_scores[first_length][second_length],
                    self._GAP_IN_SECOND,
                ),
                (
                    gap_first_scores[first_length][second_length],
                    self._GAP_IN_FIRST,
                ),
            )
        )

        aligned_first: list[str] = []
        aligned_second: list[str] = []

        first_mapping: list[int | None] = []
        second_mapping: list[int | None] = []

        i = first_length
        j = second_length

        while i > 0 or j > 0:
            if state == self._MATCH:
                if i == 0 or j == 0:
                    raise RuntimeError(
                        "Invalid match-state traceback at alignment boundary."
                    )

                previous_state = match_trace[i][j]

                aligned_first.append(first[i - 1])
                aligned_second.append(second[j - 1])

                first_mapping.append(i - 1)
                second_mapping.append(j - 1)

                i -= 1
                j -= 1

            elif state == self._GAP_IN_SECOND:
                if i == 0:
                    raise RuntimeError(
                        "Invalid gap-in-second traceback at alignment boundary."
                    )

                previous_state = gap_second_trace[i][j]

                aligned_first.append(first[i - 1])
                aligned_second.append("-")

                first_mapping.append(i - 1)
                second_mapping.append(None)

                i -= 1

            elif state == self._GAP_IN_FIRST:
                if j == 0:
                    raise RuntimeError(
                        "Invalid gap-in-first traceback at alignment boundary."
                    )

                previous_state = gap_first_trace[i][j]

                aligned_first.append("-")
                aligned_second.append(second[j - 1])

                first_mapping.append(None)
                second_mapping.append(j - 1)

                j -= 1

            else:
                raise RuntimeError(
                    f"Unknown traceback state: {state!r}."
                )

            if previous_state is None and (i > 0 or j > 0):
                raise RuntimeError(
                    "Alignment traceback ended before reaching the origin."
                )

            if previous_state is not None:
                state = previous_state

        aligned_first.reverse()
        aligned_second.reverse()

        first_mapping.reverse()
        second_mapping.reverse()

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
            final_score,
            scoring_scheme,
            gap_penalty,
        )

        return AlignmentResult(
            aligned_sequences=(
                first_result,
                second_result,
            ),
            alignment_type=AlignmentType.GLOBAL,
            score=alignment_score,
            identical_positions=identical_positions,
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
