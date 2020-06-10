var options = {
    valueNames: [ 'name', 'label', 'status']
};


var table = new List('traits-table', options);

function search(searchstring) {
  table.search(searchstring, ['name', 'label']);
}
