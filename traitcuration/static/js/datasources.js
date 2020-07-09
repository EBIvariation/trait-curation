baseUrl = '/traits/datasources/'

function makeDatasourceRequest(selectedDatasource) {
    axios
    .post(baseUrl, {'datasource': selectedDatasource})
    .then((response) => {
      // handle success
      console.log(response);
    });
}

