
package com.testforge;

import org.junit.jupiter.api.*;
import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.EnumSource;

import java.util.List;
import java.util.Optional;

import static org.junit.jupiter.api.Assertions.*;

/**
 * TestForge — Java module
 * JUnit 5 tests for a TaskManager.
 * Demonstrates: @BeforeEach, @AfterEach, @EnumSource, assertAll, Assumptions.
 */
@DisplayName("TaskManager Test Suite")
class TaskManagerTest {

    // ── domain model (inline) ─────────────────────────────────

    enum Priority   { LOW, MEDIUM, HIGH, CRITICAL }
    enum TaskStatus { TODO, IN_PROGRESS, DONE, CANCELLED }

    static class Task {
        private static int counter = 0;
        final int id;
        final String title;
        final Priority priority;
        TaskStatus status;

        Task(String title, Priority priority) {
            this.id       = ++counter;
            this.title    = title;
            this.priority = priority;
            this.status   = TaskStatus.TODO;
        }
    }

    static class TaskManager {
        private final java.util.List<Task> tasks = new java.util.ArrayList<>();

        Task add(String title, Priority priority) {
            if (title == null || title.isBlank())
                throw new IllegalArgumentException("Title must not be blank");
            Task t = new Task(title, priority);
            tasks.add(t);
            return t;
        }

        Optional<Task> findById(int id) {
            return tasks.stream().filter(t -> t.id == id).findFirst();
        }

        List<Task> findByPriority(Priority p) {
            return tasks.stream().filter(t -> t.priority == p).toList();
        }

        List<Task> findByStatus(TaskStatus s) {
            return tasks.stream().filter(t -> t.status == s).toList();
        }

        void updateStatus(int id, TaskStatus newStatus) {
            Task t = findById(id).orElseThrow(
                () -> new java.util.NoSuchElementException("Task not found: " + id));
            if (t.status == TaskStatus.DONE || t.status == TaskStatus.CANCELLED)
                throw new IllegalStateException("Cannot update a completed task");
            t.status = newStatus;
        }

        int count() { return tasks.size(); }

        List<Task> all() { return java.util.Collections.unmodifiableList(tasks); }
    }

    // ── fixtures ──────────────────────────────────────────────

    TaskManager tm;

    @BeforeEach
    void setUp() {
        Task.counter = 0; // reset ID sequence
        tm = new TaskManager();
    }

    @AfterEach
    void tearDown() {
        tm = null;
    }

    // ── adding tasks ──────────────────────────────────────────

    @Nested
    @DisplayName("add()")
    class AddTests {

        @Test
        @DisplayName("adds a task and returns it")
        void addReturnsTask() {
            Task t = tm.add("Write tests", Priority.HIGH);
            assertNotNull(t);
            assertEquals("Write tests", t.title);
        }

        @Test
        @DisplayName("task starts with TODO status")
        void newTaskIsUnstarted() {
            Task t = tm.add("Deploy app", Priority.MEDIUM);
            assertEquals(TaskStatus.TODO, t.status);
        }

        @Test
        @DisplayName("blank title throws IllegalArgumentException")
        void blankTitleThrows() {
            assertThrows(IllegalArgumentException.class,
                () -> tm.add("  ", Priority.LOW));
        }

        @Test
        @DisplayName("null title throws IllegalArgumentException")
        void nullTitleThrows() {
            assertThrows(IllegalArgumentException.class,
                () -> tm.add(null, Priority.LOW));
        }

        @Test
        @DisplayName("count increments after each add")
        void countIncrements() {
            assertEquals(0, tm.count());
            tm.add("Task A", Priority.LOW);
            assertEquals(1, tm.count());
            tm.add("Task B", Priority.HIGH);
            assertEquals(2, tm.count());
        }

        @ParameterizedTest(name = "can add task with priority {0}")
        @EnumSource(Priority.class)
        void addWithAllPriorities(Priority p) {
            Task t = tm.add("Task for " + p, p);
            assertEquals(p, t.priority);
        }
    }

    // ── finding tasks ─────────────────────────────────────────

    @Nested
    @DisplayName("findById() / findByPriority()")
    class FindTests {

        @Test
        @DisplayName("findById returns correct task")
        void findByIdFound() {
            Task added = tm.add("Fix bug", Priority.CRITICAL);
            Optional<Task> found = tm.findById(added.id);
            assertTrue(found.isPresent());
            assertEquals("Fix bug", found.get().title);
        }

        @Test
        @DisplayName("findById returns empty for unknown id")
        void findByIdNotFound() {
            assertTrue(tm.findById(9999).isEmpty());
        }

        @Test
        @DisplayName("findByPriority returns only matching tasks")
        void findByPriorityFilters() {
            tm.add("A", Priority.HIGH);
            tm.add("B", Priority.LOW);
            tm.add("C", Priority.HIGH);

            List<Task> highs = tm.findByPriority(Priority.HIGH);
            assertEquals(2, highs.size());
            assertTrue(highs.stream().allMatch(t -> t.priority == Priority.HIGH));
        }

        @Test
        @DisplayName("findByPriority returns empty list when no match")
        void findByPriorityEmpty() {
            tm.add("A", Priority.LOW);
            assertTrue(tm.findByPriority(Priority.CRITICAL).isEmpty());
        }
    }

    // ── status transitions ────────────────────────────────────

    @Nested
    @DisplayName("updateStatus()")
    class StatusTests {

        @Test
        @DisplayName("updateStatus changes task status")
        void updateStatusChanges() {
            Task t = tm.add("Review PR", Priority.MEDIUM);
            tm.updateStatus(t.id, TaskStatus.IN_PROGRESS);
            assertEquals(TaskStatus.IN_PROGRESS, t.status);
        }

        @Test
        @DisplayName("cannot update a DONE task")
        void cannotUpdateDoneTask() {
            Task t = tm.add("Closed task", Priority.LOW);
            tm.updateStatus(t.id, TaskStatus.DONE);
            assertThrows(IllegalStateException.class,
                () -> tm.updateStatus(t.id, TaskStatus.IN_PROGRESS));
        }

        @Test
        @DisplayName("cannot update a CANCELLED task")
        void cannotUpdateCancelledTask() {
            Task t = tm.add("Cancelled task", Priority.LOW);
            tm.updateStatus(t.id, TaskStatus.CANCELLED);
            assertThrows(IllegalStateException.class,
                () -> tm.updateStatus(t.id, TaskStatus.TODO));
        }

        @Test
        @DisplayName("updateStatus on unknown id throws NoSuchElementException")
        void unknownIdThrows() {
            assertThrows(java.util.NoSuchElementException.class,
                () -> tm.updateStatus(9999, TaskStatus.DONE));
        }

        @Test
        @DisplayName("all fields remain consistent after status change")
        void fieldsConsistentAfterUpdate() {
            Task t = tm.add("Multi-check task", Priority.CRITICAL);
            tm.updateStatus(t.id, TaskStatus.IN_PROGRESS);

            assertAll("task fields after status update",
                () -> assertEquals("Multi-check task", t.title),
                () -> assertEquals(Priority.CRITICAL,     t.priority),
                () -> assertEquals(TaskStatus.IN_PROGRESS, t.status)
            );
        }
    }
}
