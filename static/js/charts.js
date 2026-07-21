function getChartColors(theme) {
    const isDark = theme === "dark";
    return {
        gridColor: isDark ? "rgba(255, 255, 255, 0.08)" : "rgba(0, 0, 0, 0.06)",
        textColor: isDark ? "#94a3b8" : "#475569",
        accentPrimary: isDark ? "#6366f1" : "#4f46e5",
        accentSecondary: isDark ? "#a855f7" : "#9333ea",
        accentPrimaryAlpha: isDark ? "rgba(99, 102, 241, 0.15)" : "rgba(79, 70, 229, 0.1)",
        accentSecondaryAlpha: isDark ? "rgba(168, 85, 247, 0.15)" : "rgba(147, 51, 234, 0.1)"
    };
}

function renderProgressChart(canvasId, labels, datasetValues) {
    const canvas = document.getElementById(canvasId);
    if (!canvas) return null;

    const theme = document.documentElement.getAttribute("data-theme") || "dark";
    const colors = getChartColors(theme);

    const ctx = canvas.getContext("2d");
    return new Chart(ctx, {
        type: "line",
        data: {
            labels: labels,
            datasets: [{
                label: "Interview Score",
                data: datasetValues,
                borderColor: colors.accentPrimary,
                backgroundColor: colors.accentPrimaryAlpha,
                borderWidth: 3,
                fill: true,
                tension: 0.4,
                pointBackgroundColor: colors.accentSecondary,
                pointBorderColor: "#ffffff",
                pointHoverRadius: 6
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                }
            },
            scales: {
                x: {
                    grid: {
                        color: colors.gridColor
                    },
                    ticks: {
                        color: colors.textColor
                    }
                },
                y: {
                    grid: {
                        color: colors.gridColor
                    },
                    ticks: {
                        color: colors.textColor
                    },
                    min: 0,
                    max: 100
                }
            }
        }
    });
}

function renderRadarChart(canvasId, labels, datasetValues) {
    const canvas = document.getElementById(canvasId);
    if (!canvas) return null;

    const theme = document.documentElement.getAttribute("data-theme") || "dark";
    const colors = getChartColors(theme);

    const ctx = canvas.getContext("2d");
    return new Chart(ctx, {
        type: "radar",
        data: {
            labels: labels,
            datasets: [{
                label: "Performance Metrics",
                data: datasetValues,
                backgroundColor: colors.accentPrimaryAlpha,
                borderColor: colors.accentPrimary,
                pointBackgroundColor: colors.accentSecondary,
                pointBorderColor: "#ffffff",
                borderWidth: 2
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                }
            },
            scales: {
                r: {
                    angleLines: {
                        color: colors.gridColor
                    },
                    grid: {
                        color: colors.gridColor
                    },
                    pointLabels: {
                        color: colors.textColor,
                        font: {
                            family: "Plus Jakarta Sans",
                            size: 11
                        }
                    },
                    ticks: {
                        backdropColor: "transparent",
                        color: colors.textColor
                    },
                    min: 0,
                    max: 100
                }
            }
        }
    });
}
