<footer>
    <div class="line"></div>
    <div class="footer-content">
        <p class = 'attribution'>Created by <a href = 'https://www.michaelcahana.com' target="_blank" rel="noopener noreferrer" >Michael Cahana</a>. All code for this project can be viewed on <a href = 'https://github.com/m-cahana/nyc_towing' target="_blank" rel="noopener noreferrer" >GitHub</a>.</p>

        <h2>Methodology</h2>
        <p class = 'methodology'>
            Data on fines were scraped from New York City's <a href = 'https://data.cityofnewyork.us/resource/uvbq-3m68.json' target="_blank" rel="noopener noreferrer" >public database</a>. Data on booting/towing cases were scraped from <a href = 'https://data.cityofnewyork.us/City-Government/DOF-Scofftow-Case-Information/qmh3-uvgq/about_data' target="_blank" rel="noopener noreferrer" >NYC's Open Data Portal</a>. 
        </p>

        <p class = 'methodology'>
            Since 30,000 plates is too many to visualize, each circle shown in this project is meant to represent all plates that become scofflaws on a given day. All statistics in this project though (like the fact that 48% of scofflaws continue speeding after entering judgement) are drawn from the full distribution of plates.
        </p>

        <p class = 'methodology'>
            In order to determine when a plate entered judgement, I determined when a plate accrued over $350 in unpaid fines, and then what date would be 75 days after that moment of crossing $350. That's because, according to the <a href = 'https://www.nyc.gov/site/finance/vehicles/dispute-a-ticket-faqs.page' target="_blank" rel="noopener noreferrer" >NYC Department of Finance</a>, a camera violation goes into judgement if you don't pay or dispute it within 75 days, and a plate becomes eligible for booting/towing if it has <a href = 'https://www.nyc.gov/site/finance/vehicles/services-tickets-in-judgment.page' target="_blank" rel="noopener noreferrer" >over $350 of tickets in judgement</a>.
        </p>

        <p class = 'methodology'>
            Note that this determination of judgement is incomplete, in that I'm only considering school zone speeding violations here. In reality, plates can enter judgement from other violations too. But the focus of this project is on school zone speeding violations specifically. 
        </p>

        <p class = 'methodology'>
            To determine whether plates in judgement were later towed or booted, I simply checked whether they had any tows/boots occur after the date on which they entered judgement.
        </p>

        <p class = 'methodology'>
            Some may wonder why I didn't try to determine the share of plates entering judgement that actually get towed by the city. This would shed light on how well the city's enforcement system is working. And it'd be a very interesting metric to compute, but unfortunately because the city only reports <span class = 'italic'>whether</span> a fine gets paid, not <span class = 'italic'>when</span> it gets paid, this metric is impossible to compute with public data. 
        </p>
    </div>
</footer>

<style>
    footer {
        padding: 2rem 5%;
        margin-top: 2rem;
    }

    p {
        font-size: 14px;
        text-align: left;
    }

    .attribution {
        font-style: italic;
    }

    .methodology {
        padding-left: 1rem;
    }

    h2 {
        font-size: 18px;
        font-family: "Helvetica";
        font-weight: 300;
        font-style: italic;
        margin-bottom: 1rem;
        text-align: left;
    }

    .line {
        border-top: 1px solid black;
        width: 100%;
        margin-bottom: 1rem;
    }

    .footer-content {
        font-family: "Helvetica";
        font-weight: 300;
        text-align: center;
    }

    .italic {
        font-style: italic;
    }

</style> 