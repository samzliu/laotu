var Product = React.createClass({
      render: function() {
          return (
            <div className="home">
              <span className="homeAddress">
                {this.props.address}
              </span>
              <span className="homeDescription">
                <h1>{this.props.children}</h1>
              </span>
            </div>
          );
      }
  });

var ProductList = React.createClass({
  loadProductsFromServer: function() {
    //We're going to hard-code this information for testing purposes.
    var products = [
      {
          "address": "12345 Beverly Dr",
          "description": "This is a home in the city"
      },
      {
        "address": "98765 Tweety Ln",
        "description": "This is a home in the suburbs"
      },
      {
        "address": "1 Small St.",
        "description": "This is a nice little country home"
      },
      {
        "address": "1 Small St.",
        "description": "This is a nice little country home"
      },
      {
        "address": "1 Small St.",
        "description": "This is a nice little country home"
      },
      {
        "address": "1 Small St.",
        "description": "This is a nice little country home"
      }
    ];
    this.setState({products: products});
  },

  getInitialState: function(){
    var products = [];

    return {
      products: products
    }
  },

  componentDidMount: function() {
    this.loadProductsFromServer();
  },

  render: function() {
    var productNodes = this.state.products.map(function(product, index) {
      return (
        <Product
          key={index}
          id={index}
          address={product.address}
        >
          {product.description}
        </Product>
      );
    });
    return (
      <div className="productList">
        {productNodes}
      </div>
    );
  }
});

React.render(<ProductList />, document.getElementById('products') );

/* When the user clicks on the button,
toggle between hiding and showing the dropdown content */
function dropDownQuantity() {
    document.getElementById("myDropdown").classList.toggle("show");
}

// Close the dropdown menu if the user clicks outside of it
window.onclick = function(event) {
  if (!event.target.matches('.dropbtn')) {

    var dropdowns = document.getElementsByClassName("dropdown-content");
    var i;
    for (i = 0; i < dropdowns.length; i++) {
      var openDropdown = dropdowns[i];
      if (openDropdown.classList.contains('show')) {
        openDropdown.classList.remove('show');
      }
    }
  }
}
