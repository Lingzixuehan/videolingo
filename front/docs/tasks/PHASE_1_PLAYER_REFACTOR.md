# Issue: Refactor Player.vue Component

**Status**: In Progress
**Priority**: High
**Assignee**: Cline

## Description
The current `Player.vue` component is monolithic, containing video playback logic, subtitle rendering, tab management, and mock data processing logic. This makes it difficult to maintain and extend.

## Objectives
1.  Decompose `Player.vue` into smaller, focused components.
2.  Decouple UI logic from data processing logic (Whisper mock flow).
3.  Improve code readability and maintainability.

## Task List
- [x] Create directory `src/renderer/pages/player/`
- [x] Create `VideoPlayer.vue` (Video element, controls, overlay subtitles)
- [x] Create `PlayerSidebar.vue` (Tabs container)
- [x] Create Tab Components:
    - [x] `TabSubtitles.vue`
    - [x] `TabWords.vue`
    - [x] `TabNotes.vue`
    - [x] `TabCards.vue`
- [x] Extract Whisper mock logic into a composable `useWhisperMock.ts` (Preparation for Phase 2)
- [x] Update `Player.vue` to assemble these components.
- [ ] Verify functionality remains unchanged.

## Technical Details
- **VideoPlayer**: Should emit events for time updates and duration changes. Props: `src`, `subtitles`.
- **PlayerSidebar**: Should handle tab switching state.
- **State Management**: Continue using Pinia stores (`videos`, `subtitles`, `notes`, `cards`) to share data between components.
