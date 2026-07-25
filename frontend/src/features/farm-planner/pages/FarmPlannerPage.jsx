import React, { useState, useEffect } from "react";
import api from "../../../services/api";

const FarmPlannerPage = () => {
  const [plans, setPlans] = useState([]);
  const [activePlan, setActivePlan] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  // Form states for creating a plan
  const [cropName, setCropName] = useState("Tomato");
  const [areaAcres, setAreaAcres] = useState(1.0);
  const [plannedStartDate, setPlannedStartDate] = useState(
    new Date().toISOString().split("T")[0]
  );
  const [generating, setGenerating] = useState(false);
  const [genError, setGenError] = useState("");

  // Upcoming & Overdue lists states
  const [upcomingTasks, setUpcomingTasks] = useState([]);
  const [overdueTasks, setOverdueTasks] = useState([]);
  const [loadingTasks, setLoadingTasks] = useState(false);

  // Manual Task form states
  const [showManualForm, setShowManualForm] = useState(false);
  const [manualTitle, setManualTitle] = useState("");
  const [manualDescription, setManualDescription] = useState("");
  const [manualPlannedDate, setManualPlannedDate] = useState(
    new Date().toISOString().split("T")[0]
  );
  const [manualPriority, setManualPriority] = useState("medium");
  const [manualCategory, setManualCategory] = useState("irrigation");
  const [addingTask, setAddingTask] = useState(false);
  const [taskError, setTaskError] = useState("");

  // Timeline viewing filters
  // "all" | "overdue" | "upcoming" | "completed"
  const [timelineFilter, setTimelineFilter] = useState("all");

  useEffect(() => {
    fetchPlans();
  }, []);

  useEffect(() => {
    if (activePlan) {
      fetchUpcomingAndOverdue();
    } else {
      setUpcomingTasks([]);
      setOverdueTasks([]);
    }
  }, [activePlan]);

  const fetchPlans = async (selectLatest = true) => {
    setLoading(true);
    setError("");
    try {
      const resp = await api.get("/farm-planner/plans");
      setPlans(resp.data);
      if (resp.data.length > 0 && selectLatest) {
        // Find the active plan or default to first
        setActivePlan(resp.data[0]);
      }
    } catch (err) {
      console.error("Failed to fetch plans:", err);
      setError("Failed to load crop plans. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  const fetchUpcomingAndOverdue = async () => {
    setLoadingTasks(true);
    try {
      const [upResp, overResp] = await Promise.all([
        api.get("/farm-planner/tasks/upcoming?days=7"),
        api.get("/farm-planner/tasks/overdue"),
      ]);
      // Filter tasks belonging to the active plan specifically
      setUpcomingTasks(upResp.data.filter(t => t.farm_plan_id === activePlan.id));
      setOverdueTasks(overResp.data.filter(t => t.farm_plan_id === activePlan.id));
    } catch (err) {
      console.error("Failed to load task segments:", err);
    } finally {
      setLoadingTasks(false);
    }
  };

  const handleGeneratePlan = async (e) => {
    if (e) e.preventDefault();
    if (generating) return;

    setGenerating(true);
    setGenError("");
    try {
      const resp = await api.post("/farm-planner/plans/generate", {
        crop_name: cropName,
        area_acres: parseFloat(areaAcres),
        planned_start_date: plannedStartDate,
      });
      setActivePlan(resp.data);
      // Refresh list and select the newly generated plan
      await fetchPlans(false);
      setActivePlan(resp.data);
    } catch (err) {
      console.error("Failed to generate plan:", err);
      setGenError(
        err.response?.data?.detail || "AI Plan generation failed. Ensure soil data is logged."
      );
    } finally {
      setGenerating(false);
    }
  };

  const handleDeletePlan = async (planId) => {
    if (!window.confirm("Are you sure you want to delete this crop plan? This will delete all generated and manual tasks.")) return;
    try {
      await api.delete(`/farm-planner/plans/${planId}`);
      if (activePlan?.id === planId) {
        setActivePlan(null);
      }
      fetchPlans();
    } catch (err) {
      console.error("Failed to delete plan:", err);
      alert("Failed to delete plan.");
    }
  };

  const handleToggleComplete = async (taskId, currentStatus) => {
    try {
      const nextStatus = currentStatus === "completed" ? "pending" : "completed";
      if (nextStatus === "completed") {
        const resp = await api.patch(`/farm-planner/tasks/${taskId}/complete`);
        updateLocalTask(resp.data);
      } else {
        const resp = await api.patch(`/farm-planner/tasks/${taskId}/status`, { status: "pending" });
        updateLocalTask(resp.data);
      }
    } catch (err) {
      console.error("Failed to update task completion:", err);
    }
  };

  const handleSnooze = async (taskId, days) => {
    try {
      const resp = await api.patch(`/farm-planner/tasks/${taskId}/snooze?days=${days}`);
      updateLocalTask(resp.data);
    } catch (err) {
      console.error("Failed to postpone task:", err);
    }
  };

  const handleDeleteTask = async (taskId) => {
    if (!window.confirm("Delete this activity from your calendar?")) return;
    try {
      await api.delete(`/farm-planner/tasks/${taskId}`);
      // Remove locally
      if (activePlan) {
        const updatedTasks = activePlan.tasks.filter((t) => t.id !== taskId);
        setActivePlan({ ...activePlan, tasks: updatedTasks });
      }
      fetchUpcomingAndOverdue();
    } catch (err) {
      console.error("Failed to delete task:", err);
    }
  };

  const handleAddManualTask = async (e) => {
    if (e) e.preventDefault();
    if (!activePlan || addingTask) return;

    setAddingTask(true);
    setTaskError("");
    try {
      const resp = await api.post("/farm-planner/tasks", {
        farm_plan_id: activePlan.id,
        title: manualTitle,
        description: manualDescription,
        planned_date: manualPlannedDate,
        priority: manualPriority,
        category: manualCategory,
      });

      // Add to local state
      const updatedTasks = [...activePlan.tasks, resp.data].sort(
        (a, b) => new Date(a.planned_date) - new Date(b.planned_date)
      );
      setActivePlan({ ...activePlan, tasks: updatedTasks });

      // Reset form
      setManualTitle("");
      setManualDescription("");
      setManualPlannedDate(new Date().toISOString().split("T")[0]);
      setShowManualForm(false);
      fetchUpcomingAndOverdue();
    } catch (err) {
      console.error("Failed to add manual task:", err);
      setTaskError(err.response?.data?.detail || "Failed to create task.");
    } finally {
      setAddingTask(false);
    }
  };

  const updateLocalTask = (updatedTask) => {
    if (!activePlan) return;
    const updatedTasks = activePlan.tasks.map((t) =>
      t.id === updatedTask.id ? updatedTask : t
    );
    setActivePlan({ ...activePlan, tasks: updatedTasks });
    fetchUpcomingAndOverdue();
  };

  const categoryIcons = {
    land_preparation: "🚜",
    sowing: "🌱",
    irrigation: "💧",
    fertilizer: "🧪",
    monitoring: "🔍",
    disease_control: "🛡️",
    harvest: "🌾",
    post_harvest: "📦",
  };

  const categoryLabels = {
    land_preparation: "Land Preparation",
    sowing: "Sowing Seeds",
    irrigation: "Irrigation",
    fertilizer: "Fertilization",
    monitoring: "Crop Monitoring",
    disease_control: "Disease & Pest Control",
    harvest: "Harvesting",
    post_harvest: "Post-Harvest Operations",
  };

  const getPriorityColor = (priority) => {
    switch (priority?.toLowerCase()) {
      case "high":
        return { color: "#e53e3e", bg: "#fff5f5", border: "#f8b4b4" };
      case "medium":
        return { color: "#dd6b20", bg: "#fffaf0", border: "#fbd38d" };
      default:
        return { color: "#3182ce", bg: "#ebf8ff", border: "#bee3f8" };
    }
  };

  const getStatusColor = (status, dateStr) => {
    const today = new Date().toISOString().split("T")[0];
    if (status === "completed") return "#38a169";
    if (status === "cancelled") return "#a0aec0";
    if (status === "overdue" || dateStr < today) return "#e53e3e";
    return "#3182ce"; // pending
  };

  // Filtered timeline tasks
  const getFilteredTasks = () => {
    if (!activePlan) return [];
    let list = [...activePlan.tasks];
    const today = new Date().toISOString().split("T")[0];

    if (timelineFilter === "completed") {
      return list.filter((t) => t.status === "completed");
    }
    if (timelineFilter === "overdue") {
      return list.filter((t) => t.status !== "completed" && t.status !== "cancelled" && t.planned_date < today);
    }
    if (timelineFilter === "upcoming") {
      const next7 = new Date();
      next7.setDate(next7.getDate() + 7);
      const next7Str = next7.toISOString().split("T")[0];
      return list.filter(
        (t) =>
          t.status !== "completed" &&
          t.status !== "cancelled" &&
          t.planned_date >= today &&
          t.planned_date <= next7Str
      );
    }
    return list; // all
  };

  const filteredTasks = getFilteredTasks();

  return (
    <div
      style={{
        display: "grid",
        gridTemplateColumns: "1fr 340px",
        gap: "24px",
        padding: "32px",
        height: "calc(100vh - 100px)",
        overflow: "hidden",
      }}
    >
      {/* Left Area - Main Planner Panel */}
      <div
        style={{
          display: "flex",
          flexDirection: "column",
          gap: "24px",
          overflowY: "auto",
          paddingRight: "8px",
        }}
      >
        {/* Header Info */}
        <div className="glass" style={{ padding: "24px", borderRadius: "var(--radius-md)" }}>
          <h2 style={{ fontSize: "1.5rem", fontWeight: "800", color: "var(--text-primary)", display: "flex", alignItems: "center", gap: "10px", marginBottom: "8px" }}>
            📅 Farm Operations & Task Planner
          </h2>
          <p style={{ fontSize: "0.9rem", color: "var(--text-secondary)", margin: 0 }}>
            Generate weather-aware AI crop schedules and track day-to-day operations to optimize your yield output.
          </p>
        </div>

        {/* Generate Card if no active plan or when explicitly generating */}
        {!activePlan && (
          <div className="glass" style={{ padding: "32px 24px", borderRadius: "var(--radius-md)" }}>
            <h3 style={{ fontSize: "1.15rem", fontWeight: "700", marginBottom: "20px", color: "var(--text-primary)" }}>
              🆕 Set Up a New Crop Operations Plan
            </h3>
            <form onSubmit={handleGeneratePlan} style={{ display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: "16px" }}>
              <div style={{ display: "flex", flexDirection: "column", gap: "6px" }}>
                <label style={{ fontSize: "0.75rem", fontWeight: "700", color: "var(--text-secondary)" }}>SELECT CROP</label>
                <select
                  className="form-input"
                  value={cropName}
                  onChange={(e) => setCropName(e.target.value)}
                  style={{ width: "100%", margin: 0 }}
                >
                  {["Tomato", "Wheat", "Paddy", "Mustard", "Cotton", "Maize", "Potato", "Onion", "Sugarcane"].map((crop) => (
                    <option key={crop} value={crop}>{crop}</option>
                  ))}
                </select>
              </div>

              <div style={{ display: "flex", flexDirection: "column", gap: "6px" }}>
                <label style={{ fontSize: "0.75rem", fontWeight: "700", color: "var(--text-secondary)" }}>FARM AREA (ACRES)</label>
                <input
                  type="number"
                  className="form-input"
                  value={areaAcres}
                  onChange={(e) => setAreaAcres(e.target.value)}
                  step="0.1"
                  min="0.1"
                  style={{ width: "100%", margin: 0 }}
                />
              </div>

              <div style={{ display: "flex", flexDirection: "column", gap: "6px" }}>
                <label style={{ fontSize: "0.75rem", fontWeight: "700", color: "var(--text-secondary)" }}>PLANNED SOWING/START DATE</label>
                <input
                  type="date"
                  className="form-input"
                  value={plannedStartDate}
                  onChange={(e) => setPlannedStartDate(e.target.value)}
                  style={{ width: "100%", margin: 0 }}
                />
              </div>

              <div style={{ gridColumn: "span 3", marginTop: "12px" }}>
                <button
                  type="submit"
                  className="btn btn-primary"
                  disabled={generating}
                  style={{ width: "100%", height: "46px" }}
                >
                  {generating ? (
                    <>
                      <span className="dot-spinner"></span> Generating Crop Operations Calendar...
                    </>
                  ) : "🚀 Generate Weather & Soil Aware Schedule"}
                </button>
              </div>
            </form>

            {genError && (
              <div style={{ 
                marginTop: "16px", 
                padding: "16px", 
                backgroundColor: "var(--bg-card)", 
                color: "#e53e3e", 
                borderRadius: "var(--radius-sm)", 
                fontSize: "0.85rem", 
                border: "1px solid #e53e3e",
                borderLeft: "4px solid #e53e3e",
                display: "flex",
                alignItems: "center",
                justifyContent: "space-between",
                gap: "12px"
              }}>
                <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
                  <span>⚠️</span>
                  <span>{genError}</span>
                </div>
                <button 
                  type="button"
                  className="btn btn-primary"
                  onClick={(e) => handleGeneratePlan(e)}
                  style={{ padding: "6px 14px", fontSize: "0.75rem", flexShrink: 0 }}
                >
                  Retry
                </button>
              </div>
            )}
          </div>
        )}

        {/* Active Plan View */}
        {activePlan && (
          <div style={{ display: "flex", flexDirection: "column", gap: "24px" }}>
            
            {/* Active Plan Details Bar */}
            <div className="glass" style={{ padding: "24px", borderRadius: "var(--radius-md)", display: "flex", justifyContent: "space-between", alignItems: "center" }}>
              <div>
                <span style={{ fontSize: "0.7rem", fontWeight: "800", color: "var(--primary)", textTransform: "uppercase", letterSpacing: "0.05em" }}>
                  Active Crop Operations Plan
                </span>
                <h3 style={{ fontSize: "1.4rem", fontWeight: "900", color: "var(--text-primary)", margin: "4px 0 8px" }}>
                  🌾 {activePlan.crop_name} Plan ({activePlan.area_acres} Acres)
                </h3>
                <div style={{ display: "flex", gap: "24px", fontSize: "0.8rem", color: "var(--text-secondary)" }}>
                  <span>📅 <strong>Start Date:</strong> {new Date(activePlan.planned_start_date).toLocaleDateString()}</span>
                  <span>🌾 <strong>Est. Harvest:</strong> {new Date(activePlan.expected_harvest_date).toLocaleDateString()}</span>
                </div>
              </div>

              <div style={{ display: "flex", gap: "12px" }}>
                <button
                  className="btn"
                  onClick={() => setShowManualForm(!showManualForm)}
                  style={{
                    backgroundColor: "rgba(49, 130, 206, 0.15)",
                    color: "var(--primary)",
                    border: "1px solid rgba(49, 130, 206, 0.3)",
                    fontWeight: "700",
                  }}
                >
                  ➕ Add Custom Task
                </button>
                <button
                  className="btn"
                  onClick={() => handleDeletePlan(activePlan.id)}
                  style={{
                    backgroundColor: "rgba(229, 62, 98, 0.1)",
                    color: "#e53e3e",
                    border: "1px solid rgba(229, 62, 98, 0.2)",
                    fontWeight: "700"
                  }}
                >
                  🗑️ Delete Plan
                </button>
              </div>
            </div>

            {/* Inline Manual Task Form */}
            {showManualForm && (
              <div className="glass animate-fade-in" style={{ padding: "24px", borderRadius: "var(--radius-md)", borderLeft: "4px solid var(--primary)" }}>
                <h4 style={{ fontSize: "1rem", fontWeight: "700", marginBottom: "16px", color: "var(--text-primary)" }}>
                  ➕ Create Custom Operations Task
                </h4>
                <form onSubmit={handleAddManualTask} style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "16px" }}>
                  <div style={{ gridColumn: "span 2", display: "flex", flexDirection: "column", gap: "4px" }}>
                    <label style={{ fontSize: "0.7rem", fontWeight: "700", color: "var(--text-secondary)" }}>TASK TITLE</label>
                    <input
                      type="text"
                      className="form-input"
                      value={manualTitle}
                      onChange={(e) => setManualTitle(e.target.value)}
                      placeholder="e.g. Inspect drip irrigation tubes"
                      required
                      style={{ width: "100%", margin: 0 }}
                    />
                  </div>

                  <div style={{ gridColumn: "span 2", display: "flex", flexDirection: "column", gap: "4px" }}>
                    <label style={{ fontSize: "0.7rem", fontWeight: "700", color: "var(--text-secondary)" }}>DESCRIPTION / INSTRUCTIONS</label>
                    <textarea
                      className="form-input"
                      value={manualDescription}
                      onChange={(e) => setManualDescription(e.target.value)}
                      placeholder="Add specific agronomist recommendations or field notes..."
                      style={{ width: "100%", margin: 0, minHeight: "60px", resize: "vertical" }}
                    />
                  </div>

                  <div style={{ display: "flex", flexDirection: "column", gap: "4px" }}>
                    <label style={{ fontSize: "0.7rem", fontWeight: "700", color: "var(--text-secondary)" }}>PLANNED DATE</label>
                    <input
                      type="date"
                      className="form-input"
                      value={manualPlannedDate}
                      onChange={(e) => setManualPlannedDate(e.target.value)}
                      required
                      style={{ width: "100%", margin: 0 }}
                    />
                  </div>

                  <div style={{ display: "flex", flexDirection: "column", gap: "4px" }}>
                    <label style={{ fontSize: "0.7rem", fontWeight: "700", color: "var(--text-secondary)" }}>PRIORITY LEVEL</label>
                    <select
                      className="form-input"
                      value={manualPriority}
                      onChange={(e) => setManualPriority(e.target.value)}
                      style={{ width: "100%", margin: 0 }}
                    >
                      <option value="low">Low Priority</option>
                      <option value="medium">Medium Priority</option>
                      <option value="high">High Priority</option>
                    </select>
                  </div>

                  <div style={{ display: "flex", flexDirection: "column", gap: "4px" }}>
                    <label style={{ fontSize: "0.7rem", fontWeight: "700", color: "var(--text-secondary)" }}>CATEGORY</label>
                    <select
                      className="form-input"
                      value={manualCategory}
                      onChange={(e) => setManualCategory(e.target.value)}
                      style={{ width: "100%", margin: 0 }}
                    >
                      {Object.keys(categoryLabels).map((cat) => (
                        <option key={cat} value={cat}>{categoryLabels[cat]}</option>
                      ))}
                    </select>
                  </div>

                  <div style={{ display: "flex", gap: "12px", alignItems: "flex-end", justifyContent: "flex-end" }}>
                    <button
                      type="button"
                      className="btn"
                      onClick={() => setShowManualForm(false)}
                      style={{ flex: 1 }}
                    >
                      Cancel
                    </button>
                    <button
                      type="submit"
                      className="btn btn-primary"
                      disabled={addingTask}
                      style={{ flex: 1 }}
                    >
                      {addingTask ? "Adding..." : "Create Task"}
                    </button>
                  </div>
                </form>
                {taskError && (
                  <div style={{ marginTop: "12px", color: "#e53e3e", fontSize: "0.8rem" }}>
                    ⚠️ {taskError}
                  </div>
                )}
              </div>
            )}

            {/* Quick Summary Widgets Row */}
            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr 1fr", gap: "16px" }}>
              <div className="glass" style={{ padding: "16px", borderRadius: "var(--radius-md)", display: "flex", flexDirection: "column", gap: "4px" }}>
                <span style={{ fontSize: "0.65rem", fontWeight: "700", color: "var(--text-secondary)", textTransform: "uppercase" }}>Overdue Tasks</span>
                <strong style={{ fontSize: "1.6rem", color: overdueTasks.length > 0 ? "#e53e3e" : "var(--text-secondary)" }}>
                  {overdueTasks.length}
                </strong>
                <span style={{ fontSize: "0.65rem", color: "var(--text-muted)" }}>Action items requiring attention</span>
              </div>

              <div className="glass" style={{ padding: "16px", borderRadius: "var(--radius-md)", display: "flex", flexDirection: "column", gap: "4px" }}>
                <span style={{ fontSize: "0.65rem", fontWeight: "700", color: "var(--text-secondary)", textTransform: "uppercase" }}>Next 7 Days</span>
                <strong style={{ fontSize: "1.6rem", color: "var(--primary)" }}>
                  {upcomingTasks.length}
                </strong>
                <span style={{ fontSize: "0.65rem", color: "var(--text-muted)" }}>Upcoming planned tasks</span>
              </div>

              <div className="glass" style={{ padding: "16px", borderRadius: "var(--radius-md)", display: "flex", flexDirection: "column", gap: "4px" }}>
                <span style={{ fontSize: "0.65rem", fontWeight: "700", color: "var(--text-secondary)", textTransform: "uppercase" }}>Total Completed</span>
                <strong style={{ fontSize: "1.6rem", color: "#38a169" }}>
                  {activePlan.tasks.filter(t => t.status === "completed").length} / {activePlan.tasks.length}
                </strong>
                <span style={{ fontSize: "0.65rem", color: "var(--text-muted)" }}>Overall checklist progress</span>
              </div>
            </div>

            {/* Timeline Filter Controls */}
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", borderBottom: "1px solid var(--border-light)", paddingBottom: "12px" }}>
              <div style={{ display: "flex", gap: "8px" }}>
                {[
                  { id: "all", label: "Full Operations Timeline" },
                  { id: "overdue", label: `⚠️ Overdue (${overdueTasks.length})` },
                  { id: "upcoming", label: `📅 Next 7 Days (${upcomingTasks.length})` },
                  { id: "completed", label: "✅ Completed" },
                ].map((tab) => (
                  <button
                    key={tab.id}
                    className={`btn ${timelineFilter === tab.id ? "btn-primary" : ""}`}
                    onClick={() => setTimelineFilter(tab.id)}
                    style={{
                      padding: "6px 14px",
                      fontSize: "0.8rem",
                      borderRadius: "var(--radius-full)",
                      boxShadow: timelineFilter === tab.id ? "var(--shadow-sm)" : "none",
                      backgroundColor: timelineFilter === tab.id ? "var(--primary)" : "transparent",
                      color: timelineFilter === tab.id ? "white" : "var(--text-secondary)",
                      border: timelineFilter === tab.id ? "none" : "1px solid var(--border-light)"
                    }}
                  >
                    {tab.label}
                  </button>
                ))}
              </div>
            </div>

            {/* Vertical Timeline View */}
            {filteredTasks.length === 0 ? (
              <div className="glass" style={{ padding: "40px", textAlign: "center", color: "var(--text-secondary)", borderRadius: "var(--radius-md)" }}>
                No tasks match the active filters in this plan.
              </div>
            ) : (
              <div style={{ position: "relative", paddingLeft: "32px", display: "flex", flexDirection: "column", gap: "20px" }}>
                {/* Vertical Timeline Guide Line */}
                <div
                  style={{
                    position: "absolute",
                    left: "14px",
                    top: "16px",
                    bottom: "16px",
                    width: "2px",
                    background: "linear-gradient(to bottom, var(--primary) 0%, var(--border-light) 100%)",
                  }}
                />

                {filteredTasks.map((task) => {
                  const priStyles = getPriorityColor(task.priority);
                  const isCompleted = task.status === "completed";
                  const todayStr = new Date().toISOString().split("T")[0];
                  const isOverdue = task.status !== "completed" && task.status !== "cancelled" && task.planned_date < todayStr;
                  const markerColor = getStatusColor(task.status, task.planned_date);

                  return (
                    <div
                      key={task.id}
                      className="glass hover-card animate-fade-in"
                      style={{
                        position: "relative",
                        padding: "20px",
                        borderRadius: "var(--radius-md)",
                        display: "flex",
                        gap: "16px",
                        backgroundColor: isCompleted ? "rgba(255, 255, 255, 0.4)" : "var(--bg-card)",
                        borderLeft: isOverdue ? "4px solid #e53e3e" : (isCompleted ? "4px solid #38a169" : "1px solid var(--border-light)"),
                        opacity: isCompleted ? 0.75 : 1,
                        transition: "all 0.3s ease",
                      }}
                    >
                      {/* Timeline Dot Marker */}
                      <div
                        style={{
                          position: "absolute",
                          left: "-25px",
                          top: "24px",
                          width: "14px",
                          height: "14px",
                          borderRadius: "50%",
                          backgroundColor: markerColor,
                          border: "3px solid white",
                          boxShadow: "0 0 0 3px rgba(0,0,0,0.05)",
                          zIndex: 2,
                        }}
                      />

                      {/* Checkbox wrapper */}
                      <div style={{ display: "flex", alignItems: "flex-start", paddingTop: "2px" }}>
                        <input
                          type="checkbox"
                          checked={isCompleted}
                          onChange={() => handleToggleComplete(task.id, task.status)}
                          style={{
                            width: "20px",
                            height: "20px",
                            cursor: "pointer",
                            accentColor: "#38a169",
                          }}
                        />
                      </div>

                      {/* Content panel */}
                      <div style={{ flex: 1, display: "flex", flexDirection: "column", gap: "6px" }}>
                        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start" }}>
                          <div>
                            <span style={{ fontSize: "0.65rem", fontWeight: "700", color: "var(--text-muted)", display: "flex", alignItems: "center", gap: "4px" }}>
                              <span>{categoryIcons[task.category] || "📅"}</span>
                              <span>{categoryLabels[task.category] || task.category}</span>
                            </span>
                            <h4
                              style={{
                                fontSize: "1.05rem",
                                fontWeight: "800",
                                color: "var(--text-primary)",
                                textDecoration: isCompleted ? "line-through" : "none",
                                color: isCompleted ? "var(--text-muted)" : "var(--text-primary)",
                                margin: "2px 0 0",
                              }}
                            >
                              {task.title}
                            </h4>
                          </div>

                          <div style={{ display: "flex", gap: "6px", alignItems: "center" }}>
                            {/* Priority Badge */}
                            <span
                              style={{
                                fontSize: "0.6rem",
                                fontWeight: "800",
                                textTransform: "uppercase",
                                padding: "2px 8px",
                                borderRadius: "4px",
                                color: priStyles.color,
                                backgroundColor: priStyles.bg,
                                border: `1px solid ${priStyles.border}`,
                              }}
                            >
                              {task.priority}
                            </span>
                            
                            {/* Date Badge */}
                            <span
                              style={{
                                fontSize: "0.7rem",
                                fontWeight: "700",
                                color: isOverdue ? "#e53e3e" : "var(--text-secondary)",
                              }}
                            >
                              {isOverdue ? "⚠️ Overdue: " : ""}
                              {new Date(task.planned_date).toLocaleDateString()}
                            </span>
                          </div>
                        </div>

                        <p
                          style={{
                            fontSize: "0.85rem",
                            color: "var(--text-secondary)",
                            lineHeight: "1.4",
                            margin: 0,
                          }}
                        >
                          {task.description}
                        </p>

                        {/* Quick action row */}
                        {!isCompleted && (
                          <div style={{ display: "flex", gap: "10px", marginTop: "10px", borderTop: "1px solid rgba(0,0,0,0.03)", paddingTop: "10px" }}>
                            <button
                              onClick={() => handleSnooze(task.id, 1)}
                              style={{
                                fontSize: "0.7rem",
                                backgroundColor: "rgba(0,0,0,0.03)",
                                border: "1px solid var(--border-light)",
                                borderRadius: "4px",
                                padding: "4px 8px",
                                cursor: "pointer",
                                color: "var(--text-secondary)"
                              }}
                            >
                              💤 Postpone 1 Day
                            </button>
                            <button
                              onClick={() => handleSnooze(task.id, 3)}
                              style={{
                                fontSize: "0.7rem",
                                backgroundColor: "rgba(0,0,0,0.03)",
                                border: "1px solid var(--border-light)",
                                borderRadius: "4px",
                                padding: "4px 8px",
                                cursor: "pointer",
                                color: "var(--text-secondary)"
                              }}
                            >
                              💤 Postpone 3 Days
                            </button>
                            <button
                              onClick={() => handleDeleteTask(task.id)}
                              style={{
                                fontSize: "0.7rem",
                                backgroundColor: "rgba(229, 62, 98, 0.05)",
                                border: "1px solid rgba(229, 62, 98, 0.15)",
                                borderRadius: "4px",
                                padding: "4px 8px",
                                cursor: "pointer",
                                color: "#e53e3e",
                                marginLeft: "auto",
                              }}
                            >
                              🗑️ Delete
                            </button>
                          </div>
                        )}
                      </div>
                    </div>
                  );
                })}
              </div>
            )}
          </div>
        )}
      </div>

      {/* Right Sidebar - Crop Plan History */}
      <div
        className="glass"
        style={{
          borderRadius: "var(--radius-md)",
          padding: "24px 16px",
          display: "flex",
          flexDirection: "column",
          gap: "16px",
          overflowY: "hidden",
        }}
      >
        <h3
          style={{
            fontSize: "1.1rem",
            padding: "0 8px",
            color: "var(--text-primary)",
            borderBottom: "1px solid var(--border-light)",
            paddingBottom: "12px",
            margin: 0,
          }}
        >
          📋 Active Crop Plans
        </h3>

        <div
          style={{
            display: "flex",
            flexDirection: "column",
            gap: "12px",
            overflowY: "auto",
            flex: 1,
            padding: "2px",
          }}
        >
          {loading ? (
            <div style={{ textAlign: "center", padding: "40px", color: "var(--text-secondary)", fontSize: "0.875rem" }}>
              <span className="dot-spinner"></span> Loading plans...
            </div>
          ) : plans.length === 0 ? (
            <div style={{ textAlign: "center", padding: "40px", color: "var(--text-secondary)", fontSize: "0.875rem" }}>
              No crop plans generated yet. Use the scheduler to create one!
            </div>
          ) : (
            plans.map((p) => {
              const isActive = activePlan?.id === p.id;
              return (
                <div
                  key={p.id}
                  onClick={() => {
                    setActivePlan(p);
                    setTimelineFilter("all");
                    setShowManualForm(false);
                  }}
                  className={`glass hover-card ${isActive ? "active-plan" : ""}`}
                  style={{
                    padding: "14px",
                    borderRadius: "var(--radius-sm)",
                    cursor: "pointer",
                    backgroundColor: isActive ? "rgba(49, 130, 206, 0.1)" : "var(--bg-card)",
                    borderLeft: isActive ? "4px solid var(--primary)" : "1px solid var(--border-light)",
                    transition: "var(--transition-smooth)",
                  }}
                >
                  <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                    <strong style={{ fontSize: "0.875rem", color: "var(--text-primary)" }}>
                      🌾 {p.crop_name}
                    </strong>
                    <span style={{ fontSize: "0.7rem", color: "var(--text-secondary)", fontWeight: "700" }}>
                      {p.area_acres} ac
                    </span>
                  </div>
                  <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginTop: "8px", borderTop: "1px solid rgba(0,0,0,0.03)", paddingTop: "6px" }}>
                    <span style={{ fontSize: "0.7rem", color: "var(--text-muted)" }}>
                      Sown: {new Date(p.planned_start_date).toLocaleDateString()}
                    </span>
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        handleDeletePlan(p.id);
                      }}
                      style={{
                        background: "transparent",
                        border: "none",
                        fontSize: "0.8rem",
                        cursor: "pointer",
                        padding: 0,
                      }}
                      title="Delete plan"
                    >
                      🗑️
                    </button>
                  </div>
                </div>
              );
            })
          )}
        </div>

        {/* Action button to trigger new plan form */}
        {activePlan && (
          <button
            className="btn btn-primary"
            onClick={() => {
              setActivePlan(null);
              setShowManualForm(false);
            }}
            style={{ width: "100%", height: "42px", display: "flex", alignItems: "center", justifyContent: "center", gap: "8px" }}
          >
            🌱 Schedule New Crop
          </button>
        )}
      </div>
    </div>
  );
};

export default FarmPlannerPage;
