"use client"
import React, { useState } from 'react';


export default function MyInput(){
    const [inputValue, setInputValue] = React.useState('');

    const handleInputChange = (event)=> {
        setInputValue(event.target.value);
    }

    return (
        <div>
            <label htmlFor="my-inpuy">Enter text:</label>
            <input type="text" id="my-input" value={inputValue} onChange={handleInputChange}/>
            <p>You entered: {inputValue}</p>
        </div>
    )
}