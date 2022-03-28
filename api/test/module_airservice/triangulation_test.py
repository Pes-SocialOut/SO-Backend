# -*- coding: utf-8 -*-
import pytest
from app.module_airservice.jobs.triangulation import distance_based_weighted_mean
from app.module_airservice.controllers import barycentric_interpolation

# Estos tests solo comprueban partes no triviales de la triangulación.
class TestTriangulationAlgorithmSuite:

    def test_vertical_distance_based_weighted_mean(self):
        # Arrange
        data = [
            (-1, 0, 0, -1),
            (-1, 0, -1, -5),
            (-1, 0, 2, 5)
        ]
        adjacencies = [1,2]
        
        # Action
        res = distance_based_weighted_mean(data, 0, adjacencies)
        
        # Assert
        assert res == -5/3
    
    def test_horizontal_distance_based_weighted_mean(self):
        # Arrange
        data = [
            (-1, 0, 0, -1),
            (-1, 3, 0, 0),
            (-1, -1, 0, 1)
        ]
        adjacencies = [1,2]
        
        # Action
        res = distance_based_weighted_mean(data, 0, adjacencies)
        
        # Assert
        assert res == 3/4
    
    def test_oblique_distance_based_weighted_mean(self):
        # Arrange
        data = [
            (-1, 0, 0, -1),
            (-1, -4, 2, 0),
            (-1, 1, -2, 1)
        ]
        adjacencies = [1,2]
        
        # Action
        res = distance_based_weighted_mean(data, 0, adjacencies)
        
        # Assert
        assert res == 2/3
    
    def test_barycentric_interpolation_on_v0(self):
        # Arrange
        v0x = 0; v0y = 0
        v1x = 1; v1y = 3
        v2x = 5; v2y = 1
        px  = 0; py  = 0
        # Action
        w0, w1, w2 = barycentric_interpolation(v0x, v0y, v1x, v1y, v2x, v2y, px, py)
        # Assert
        assert w0 == 1
        assert w1 == 0
        assert w2 == 0
    
    def test_barycentric_interpolation_on_v1(self):
        # Arrange
        v0x = 0; v0y = 0
        v1x = 1; v1y = 3
        v2x = 5; v2y = 1
        px  = 1; py  = 3
        # Action
        w0, w1, w2 = barycentric_interpolation(v0x, v0y, v1x, v1y, v2x, v2y, px, py)
        # Assert
        assert w0 == 0
        assert w1 == 1
        assert w2 == 0
    
    def test_barycentric_interpolation_on_v2(self):
        # Arrange
        v0x = 0; v0y = 0
        v1x = 1; v1y = 3
        v2x = 5; v2y = 1
        px  = 5; py  = 1
        # Action
        w0, w1, w2 = barycentric_interpolation(v0x, v0y, v1x, v1y, v2x, v2y, px, py)
        # Assert
        assert w0 == 0
        assert w1 == 0
        assert w2 == 1
    
    def test_barycentric_interpolation_on_v0_v1_mean(self):
        # Arrange
        v0x = 0; v0y = 0
        v1x = 1; v1y = 3
        v2x = 5; v2y = 1
        px  =.5; py  = 1.5
        # Action
        w0, w1, w2 = barycentric_interpolation(v0x, v0y, v1x, v1y, v2x, v2y, px, py)
        # Assert
        assert w0 == .5
        assert w1 == .5
        assert w2 == 0
    
    def test_barycentric_interpolation_on_v0_v2_mean(self):
        # Arrange
        v0x = 0; v0y = 0
        v1x = 1; v1y = 3
        v2x = 5; v2y = 1
        px  =2.5; py =.5
        # Action
        w0, w1, w2 = barycentric_interpolation(v0x, v0y, v1x, v1y, v2x, v2y, px, py)
        # Assert
        assert w0 == .5
        assert w1 == 0
        assert w2 == .5
    
    def test_barycentric_interpolation_on_v1_v2_mean(self):
        # Arrange
        v0x = 0; v0y = 0
        v1x = 1; v1y = 3
        v2x = 5; v2y = 1
        px  = 3; py  = 2
        # Action
        w0, w1, w2 = barycentric_interpolation(v0x, v0y, v1x, v1y, v2x, v2y, px, py)
        # Assert
        assert w0 == 0
        assert w1 == .5
        assert w2 == .5

    def test_barycentric_interpolation_on_barycenter(self):
        # Arrange
        v0x = 0; v0y = 0
        v1x = 1; v1y = 3
        v2x = 5; v2y = 1
        px  = 2; py  = 4/3
        # Action
        w0, w1, w2 = barycentric_interpolation(v0x, v0y, v1x, v1y, v2x, v2y, px, py)
        # Assert
        one_third = round(1/3, 15)
        assert round(w0, 15) == one_third
        assert round(w1, 15) == one_third
        assert round(w2, 15) == one_third