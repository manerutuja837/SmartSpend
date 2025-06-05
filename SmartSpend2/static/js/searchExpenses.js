const searchField = document.querySelector('#SearchField');
const appTable = document.querySelector('.app-table');
const tbody = document.querySelector('.table-body');
const paginationContainer = document.querySelector('.pagination-container');
const tableOutput = document.querySelector('.table-output');
tableOutput.style.display = "none";

searchField.addEventListener("keyup",(e) => {
    const searchValue = e.target.value;

    if(searchValue.length > 0){
        paginationContainer.style.display = "none";
        tbody.innerHTML = "";
        console.log('searchValue', searchValue);

        fetch("/search_expenses/", {
            body: JSON.stringify({ searchText: searchValue }),
            method: "POST",
          })
            .then((res) => res.json())
            .then((data) => {
                  console.log("data",data);
                  appTable.style.display = "none";
                  tableOutput.style.display = "block";
                  if(data.length === 0){
                    tableOutput.innerHTML = "No Results Found";
                  }else{
                    data.forEach((item) => {
                        tbody.innerHTML += `<tr>
                        <td>${item.amount}</td>
                        <td>${item.category}</td>
                        <td>${item.description}</td>
                        <td>${item.date}</td>
                        </tr>`;
                    });
                  }

              });

    }else{
        tableOutput.style.display = "none";
        appTable.style.display = "block";
        paginationContainer.style.display = "block";
    }
})