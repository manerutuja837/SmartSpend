const renderChart = (data,labels) =>{
    const ctx = document.getElementById('myChart');

new Chart(ctx, {
    type: 'bar',
    data: {
    labels: labels,
    datasets: [{
        label: 'Last Month Expenses',
        data: data,
        borderWidth: 1
    }]
    },
    options: {
        title:{
            display:true,
            text:'Expense per Category',
        }
    },
});
}

const getChartData = ()=>{
    console.log('fetching');
    fetch('/expense_category_summary')
    .then(res=>res.json())
    .then(results=>{
        console.log('results', results);
        const category_data = results.expense_category_data;
        const [labels, data] = [Object.keys(category_data),Object.values(category_data),
        ];
        renderChart(data, labels);
    });
};

document.onload = getChartData();