<script>
    import { onMount } from "svelte";
    import { getFullPath } from "$lib/utils/paths";
    import * as d3 from "d3";
  
    let {
      dataPath = "/data/bar_plot_data.csv",
      width = 800,
      height = 600,
    } = $props();
  
    let data = [];
  
    function createVisualization(container, data, width, height) {
      const margin = { top: 50, right: 30, bottom: 90, left: 70 };
      const innerWidth = width - margin.left - margin.right;
      const innerHeight = height - margin.top - margin.bottom;
  
      // Remove existing SVG
      d3.select(container).selectAll("*").remove();
  
      // Root SVG with *explicit px dimensions*
      const svg = d3
        .select(container)
        .append("svg")
        .attr("width", width)
        .attr("height", height);
  
      const g = svg
        .append("g")
        .attr("transform", `translate(${margin.left},${margin.top})`);
  
      // Scales
      const x = d3
        .scaleBand()
        .range([0, innerWidth])
        .domain(data.map((d) => d.violations_bin))
        .padding(0.2);
  
      const y = d3
        .scaleLinear()
        .range([innerHeight, 0])
        .domain([0, d3.max(data, (d) => d.share_of_fines_paid)]);
  
      // Axes
      g.append("g")
        .attr("class", "axis")
        .attr("transform", `translate(0,${innerHeight})`)
        .call(d3.axisBottom(x))
        .selectAll("text")
        .attr("transform", "translate(-10,0)rotate(-45)")
        .style("text-anchor", "end");
  
      g.append("g")
        .attr("class", "axis")
        .call(d3.axisLeft(y).ticks(5).tickFormat((d) => d + "%"));

  
      // Bars
      g.selectAll("rect")
        .data(data)
        .enter()
        .append("rect")
        .attr("x", (d) => x(d.violations_bin))
        .attr("width", x.bandwidth())
        .attr("y", innerHeight)
        .attr("height", 0)
        .attr("class", "bar")
        .attr("fill", "#305cde")
        .on("mouseover", function (event, d) {
          d3.select("#tooltip")
            .style("opacity", 1)
            .html(
              `<strong>School zone violations:</strong> ${d.violations_bin}<br><strong>Share of fines paid:</strong> ${d.share_of_fines_paid.toFixed(
                1
              )}%`
            )
            .style("left", `${event.clientX + 15}px`)
            .style("top", `${event.clientY - 40}px`);
        })
        .on("mouseout", function () {
          d3.select("#tooltip").style("opacity", 0);
        })
        .transition()
        .duration(1000)
        .attr("y", (d) => y(d.share_of_fines_paid))
        .attr("height", (d) => innerHeight - y(d.share_of_fines_paid));
  
      // Titles and labels (true px font sizes!)
      const titleGroup = svg
        .append("g")
        .attr("class", "chart-title")
        .attr("text-anchor", "middle")
        .attr("transform", `translate(${width / 2}, ${margin.top / 2})`);
      
      if (width <= 600) {
        // Two lines for small screens
        titleGroup
          .append("text")
          .attr("y", "-8")
          .text("Drivers are less likely to pay fines");
        titleGroup
          .append("text")
          .attr("y", "8")
          .text("the more they speed");
      } else {
        // Single line for larger screens
        titleGroup
          .append("text")
          .attr("y", "0")
          .text("Drivers are less likely to pay fines the more they speed");
      }
  
      svg
        .append("text")
        .attr("class", "x-axis-label")
        .attr("text-anchor", "middle")
        .attr("x", width / 2)
        .attr("y", height - margin.bottom / 3)
        .text("School Zone Violations");
  
      svg
        .append("text")
        .attr("class", "y-axis-label")
        .attr("text-anchor", "middle")
        .attr("transform", "rotate(-90)")
        .attr("x", -height / 2)
        .attr("y", margin.left / 3)
        .text("Share of Fines Paid");
    }
  
    onMount(() => {
      const fullDataPath = getFullPath(dataPath);
  
      d3.csv(fullDataPath)
        .then((rawData) => {
          data = rawData.map((d) => ({
            ...d,
            share_of_fines_paid: +d.share_of_fines_paid,
          }));
          return data;
        })
        .then((data) => {
          const container = document.getElementById("barplot-container");
  
          // Initial draw
          createVisualization(container, data, width, height);
  
          // ResizeObserver for responsiveness
          const resizeObserver = new ResizeObserver((entries) => {
            for (let entry of entries) {
              const newWidth = entry.contentRect.width;
              const aspect = height / width;
              const newHeight = newWidth * aspect;
              createVisualization(container, data, newWidth, newHeight);
            }
          });
          resizeObserver.observe(container);
        })
        .catch((error) => {
          console.error("Error loading CSV:", error);
        });
    });
  </script>
  
  <div id="barplot-container" style="width: 100%;"></div>
  <div id="tooltip"></div>
  
  <style>
    #barplot-container {
      width: 100%;
      height: auto;
    }
  
    :global(.bar) {
      transition: fill 0.2s ease;
    }
  
    :global(.bar:hover) {
      fill: var(--dark-blue);
    }
  
    :global(.axis text) {
      font-family: Helvetica, Arial, sans-serif;
      font-weight: 300;
      font-size: clamp(10px, 1.5vw, 14px) !important; /* Override D3's inline styles */
    }
  
    :global(.chart-title) {
      font-family: Helvetica, Arial, sans-serif;
      font-weight: 300;
      font-size: clamp(16px, 2vw, 20px); /* fixed px */
    }
  
    :global(.x-axis-label),
    :global(.y-axis-label) {
      font-family: Helvetica, Arial, sans-serif;
      font-weight: 300;
      font-size: clamp(14px, 1.5vw, 18px); /* fixed px */
    }
  
    :global(#tooltip) {
      opacity: 0;
      transition: opacity 0.2s;
      font-size: 14px;
      font-family: "Helvetica", sans-serif;
      text-align: left;
      position: fixed;
      background-color: white;
      color: black;
      border-radius: 5px;
      box-shadow: 0 0 10px rgba(0, 0, 0, 0.25);
      border: 1px solid rgba(0, 0, 0, 0.1);
      padding: 10px;
      pointer-events: none;
      font-weight: 300;
      z-index: 9999;
      min-width: 200px;
      max-width: 300px;
    }

  </style>