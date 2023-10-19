import React, { useState } from 'react';
import './index.css';
// import AWS from 'aws-sdk';


function App() {

  const [showForm, setShowForm] = useState(false);
  const [obituaries, setObituaries] = useState([]);

  const handleNewObituaryClick = () => {
    setShowForm(true);
  };

  const handleCloseFormClick = () => {
    setShowForm(false);
  };

  const handleObituarySubmit = async (event) => {
    event.preventDefault();

    // Create a new FormData object from the form data
    const formData = new FormData(event.target);

    // Create a new obituary object with the form data
    const newObituary = {
      name: formData.get('name'),
      birthDate: formData.get('date-of-birth'),
      deathDate: formData.get('date-of-death'),
      photo: formData.get('photo')
    };

    // Update the obituaries state with the new obituary
    setObituaries([...obituaries, newObituary]);

    try 
    {
      // Send a POST request to the API with the form data
      const res = await fetch(
        "/",
        {
          method: "POST",
          body: formData,
        }
      );
    } 
    catch (err) 
    {
      console.error(err);
    }

    // Close the form
    setShowForm(false);
  };

  return (
    <div className="App">
      <div className="header">
        <h1 className="title">The Last Show</h1>
        <button className="new-obituary-button" onClick={handleNewObituaryClick}>+ New Obituary</button>
      </div>
      <hr className="line" />
      {showForm ? (
        <div className="form-container">
          <button className="close-button" onClick={handleCloseFormClick}>X</button>
          <form onSubmit={handleObituarySubmit}>
            <label htmlFor="photo">Image of the Deceased:</label>
            <input type="file" id="photo" name="photo" accept=".jpg, .jpeg, .png" required />

            <label htmlFor="name">Name:</label>
            <input type="text" id="name" name="name" required />

            <label htmlFor="date-of-birth">Date of Birth:</label>
            <input type="date" id="date-of-birth" name="date-of-birth" required />


            <label htmlFor="date-of-death">Date of Death:</label>
            <input type="date" id="date-of-death" name="date-of-death" required />


            <button type="submit">Write Obituary</button>
          </form>
          </div>
  ) : (
    <div className="body-container">
      {obituaries.length > 0 ? (
        obituaries.map((obituary, index) => (
          <div className="obituary-container" key={index}>
            <img src={obituary.photo} alt={obituary.name} />
            <div className="info">
              <h2 className="name">{obituary.name}</h2>
              <p className="date">{obituary.birthDate} - {obituary.deathDate}</p>

            </div>
          </div>
        ))
      ) : (
        <div className="body">No Obituary Yet.</div>
      )}
    </div>
  )}
</div>
);
}

export default App;
