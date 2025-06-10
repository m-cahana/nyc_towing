<script>
    import { onMount } from 'svelte';
    import Scrolly from "$lib/components/helpers/scrolly.svelte";
    import { getFullPath } from '$lib/utils/paths';
    import * as d3 from 'd3';

    // Props for the component
    let {
        dataPath = '/data/bar_plot_data.csv',
        width = 800,
        height = 600,
    } = $props();

    let data = [];

    // Function to create the bar plot visualization
    function createVisualization(data) {
        // Set the dimensions and margins of the graph
        const margin = {top: 30, right: 30, bottom: 90, left: 60};
        const innerWidth = width - margin.left - margin.right;
        const innerHeight = height - margin.top - margin.bottom;

        // Remove any existing SVG
        d3.select("#barplot-container").selectAll("*").remove();

        // Create the SVG container
        const svg = d3.select("#barplot-container")
            .append("svg")
            .attr("width", width)
            .attr("height", height)
            .append("g")
            .attr("transform", `translate(${margin.left},${margin.top})`);

        // Add title
        svg.append("text")
            .attr("class", "chart-title")
            .attr("text-anchor", "middle")
            .attr("x", innerWidth / 2)
            .attr("y", -margin.top / 2)
            .text("Drivers are less likely to pay fines the more they speed");

        // X axis
        const x = d3.scaleBand()
            .range([0, innerWidth])
            .domain(data.map(d => d.violations_bin))
            .padding(0.2);

        // Y axis
        const y = d3.scaleLinear()
            .range([innerHeight, 0])
            .domain([0, d3.max(data, d => d.share_of_fines_paid)]);

        // Add X axis
        svg.append("g")
            .attr("class", "axis")
            .attr("transform", `translate(0,${innerHeight})`)
            .call(d3.axisBottom(x))
            .selectAll("text")
            .attr("transform", "translate(-10,0)rotate(-45)")
            .style("text-anchor", "end");

        // Add Y axis
        svg.append("g")
            .attr("class", "axis")
            .call(d3.axisLeft(y).ticks(5).tickFormat(d => d + "%"));

        // Add X axis label
        svg.append("text")
            .attr("class", "axis-label")
            .attr("text-anchor", "middle")
            .attr("x", innerWidth / 2)
            .attr("y", innerHeight + margin.bottom - 30)
            .text("School Zone Violations");

        // Add Y axis label
        svg.append("text")
            .attr("class", "axis-label")
            .attr("text-anchor", "middle")
            .attr("transform", "rotate(-90)")
            .attr("y", -margin.left + 20)
            .attr("x", -innerHeight / 2)
            .text("Share of Fines Paid");

        // Add the bars
        svg.selectAll("rect")
            .data(data)
            .enter()
            .append("rect")
            .attr("x", d => x(d.violations_bin))
            .attr("width", x.bandwidth())
            .attr("y", innerHeight)
            .attr("height", 0)
            .attr("class", "bar")
            .attr("fill", "#305cde")
            .on("mouseover", function(event, d) {
                d3.select("#tooltip")
                    .style("opacity", 1)
                    .html(`<strong>School zone violations:</strong> ${d.violations_bin}<br><strong>Share of fines paid:</strong> ${d.share_of_fines_paid.toFixed(1)}%`)
                    .style("left", `${event.clientX + 15}px`)
                    .style("top", `${event.clientY - 40}px`);
            })
            .on("mouseout", function() {
                d3.select("#tooltip")
                    .style("opacity", 0);
            })
            .transition()
            .duration(1000)
            .attr("y", d => y(d.share_of_fines_paid))
            .attr("height", d => innerHeight - y(d.share_of_fines_paid));
    }

    onMount(() => {
        // Use our utility function to handle the path from props
        const fullDataPath = getFullPath(dataPath);
        console.log(`Loading data from: ${fullDataPath}`);
        
        // Load and process the data
        d3.csv(fullDataPath)
            .then(rawData => {
                // Convert string values to numbers
                data = rawData.map(d => ({
                    ...d,
                    share_of_fines_paid: +d.share_of_fines_paid
                }));
                return data;
            })
            .then(createVisualization)
            .catch((error) => {
                console.error("Error loading CSV:", error);
            });
    });
</script>

<div id="barplot-container" style="width: 100%; height: 100%;"></div>
<div id="tooltip"></div>

<style>
    #barplot-container {
        width: 100%;
        height: 100%;
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
        font-size: 14px;
    }

    :global(.axis-label) {
        font-family: Helvetica, Arial, sans-serif;
        font-weight: 300;
        font-size: 18px;
    }

    :global(.chart-title) {
        font-family: Helvetica, Arial, sans-serif;
        font-weight: 300;
        font-size: 20px;
    }
  /* Tooltip styles */
  :global(#tooltip) {
        opacity: 0;
        transition: opacity 0.2s;
        font-size: 14px;
        font-family: 'Helvetica', sans-serif;
        text-align: left;
        position: fixed;
        background-color: white;
        color: black;
        border-radius: 5px;
        box-shadow: 0 0 10px rgba(0,0,0,0.25);
        border: 1px solid rgba(0,0,0,0.1);
        padding: 10px;
        pointer-events: none;
        font-weight: 300;
        z-index: 9999; /* Ensure tooltip is always on top */
        min-width: 200px;
        max-width: 300px;
    }
</style>
